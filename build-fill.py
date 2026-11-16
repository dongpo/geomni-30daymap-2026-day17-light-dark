from pathlib import Path
import json,subprocess,shutil,hashlib
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
P=Path(__file__).resolve().parent; O=P/'base-data'
for f in ['metadata.json','terrain-info.json'] : shutil.copy(O/f,P/f)
shutil.copy(O/'normals.png',P/'normals-original.png')
j=json.loads((O/'terrain-info.json').read_text());w,h=j['size'];g=j['geoTransform'];dx,dy=g[1],-g[5]
(P/'target.wkt').write_text(j['coordinateSystem']['wkt'])
def run(a):subprocess.run(a,check=True,capture_output=True)
run(['gdalwarp','-overwrite','-t_srs',str(P/'target.wkt'),'-te',str(g[0]),str(g[3]-h*dy),str(g[0]+w*dx),str(g[3]),'-ts',str(w),str(h),'-r','average','-dstnodata','-32767','-co','COMPRESS=DEFLATE',str(P/'source/copernicus-n24-e121.tif'),str(P/'copernicus-aligned.tif')])
run(['gdal_translate','-of','ENVI',str(P/'copernicus-aligned.tif'),str(P/'copernicus.bin')])
z=np.fromfile(O/'terrain.bin',dtype='<f4').reshape(h,w);c=np.fromfile(P/'copernicus.bin',dtype='<f4').reshape(h,w);valid=z!=-32767
lab,num=ndi.label(~valid);hole=lab==lab[883,1063];assert lab[883,1063]>0 and not hole[0].any() and not hole[-1].any()
assert (c[hole]!=-32767).all()
dist=ndi.distance_transform_edt(~hole);ring=(dist>0)&(dist<=20)&valid&(c!=-32767)
diff=z[ring]-c[ring];bias=float(np.median(diff));filled=z.copy();filled[hole]=c[hole]+bias
assert np.array_equal(filled[~hole],z[~hole])
filled.astype('<f4').tofile(P/'terrain-filled.bin');shutil.copy(O/'terrain.hdr',P/'terrain-filled.hdr')
run(['gdal_translate','-of','GTiff','-co','COMPRESS=DEFLATE',str(P/'terrain-filled.bin'),str(P/'terrain-filled.tif')])
Image.fromarray(np.uint8(hole)*255).save(P/'fill-mask.png')
ys,xs=np.where(hole)
# Derive identical Horn slope normals from filled DEM.
z=filled;valid=z!=-32767;q=np.pad(z,1,mode='edge');mv=np.pad(valid,1);mask=np.ones(z.shape,bool)
for y in range(3):
 for x in range(3):mask &= mv[y:y+h,x:x+w]
gx=((q[:-2,2:]+2*q[1:-1,2:]+q[2:,2:])-(q[:-2,:-2]+2*q[1:-1,:-2]+q[2:,:-2]))/(8*dx)
gy=((q[:-2,:-2]+2*q[:-2,1:-1]+q[:-2,2:])-(q[2:,:-2]+2*q[2:,1:-1]+q[2:,2:]))/(8*dy)
n=np.stack([-gx,-gy,np.ones(z.shape)],-1);n/=np.linalg.norm(n,axis=-1)[...,None];n[~mask]=[0,0,1]
a=np.zeros((h,w,4),np.uint8);a[:,:,:3]=np.rint((n+1)*127.5);a[:,:,3]=mask*255;Image.fromarray(a).save(P/'normals.png')
def stats(d):return {'n':int(d.size),'median_m':float(np.median(d)),'mae_m':float(np.mean(abs(d))),'rmse_m':float(np.sqrt(np.mean(d*d))),'p05_p95_m':np.percentile(d,[5,95]).tolist()}
# cross-boundary elevation steps, natural slope included; NOT positional/vertical accuracy.
steps=[]
for axis in [0,1]:
 a1=[slice(None)]*2;a2=a1.copy();a1[axis]=slice(1,None);a2[axis]=slice(None,-1);a1=tuple(a1);a2=tuple(a2)
 edge=(hole[a1]!=hole[a2])&valid[a1]&valid[a2];steps.extend((z[a1]-z[a2])[edge])
qa={'date':'2026-11-16','filled_cells':int(hole.sum()),'filled_area_km2':float(hole.sum()*dx*dy/1e6),'ring_width_approx_m':2000,'overlap_raw':stats(diff),'constant_bias_added_m':bias,'overlap_after_bias':stats(diff-bias),'boundary_steps_including_natural_slope':stats(np.array(steps)),'original_valid_cells_unchanged':True,'other_nodata_unchanged':True,'fill_method':'GLO30 average resampling to existing 100m grid, plus median Taiwan-minus-GLO30 overlap offset; only selected enclosed source NoData component','accuracy_in_hole':'No independent reference; not verified','source_sha256':hashlib.sha256((P/'source/copernicus-n24-e121.tif').read_bytes()).hexdigest()}
(P/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
m=json.loads((P/'metadata.json').read_text());m['places']=[p for p in m['places'] if p['name']!='來源缺值'];m['places'].append({'name':'補值區','u':float(xs.mean()/w),'v':float(ys.mean()/h)});m['fill_bbox']=[float(xs.min()/w),float(ys.min()/h),float((xs.max()+1)/w),float((ys.max()+1)/h)];m['qa_fill']=qa;(P/'metadata.json').write_text(json.dumps(m,ensure_ascii=False))
print(json.dumps(qa,ensure_ascii=False,indent=2))

e=hole&~ndi.binary_erosion(hole);rgba=np.zeros((*hole.shape,4),np.uint8);rgba[e]=[255,189,77,240];Image.fromarray(rgba).save(P/'fill-outline.png')
