# Day17 — Light & dark

[互動地圖](https://dongpo.github.io/geomni-30daymap-2026-day17-light-dark/) · [操作影片](video/day17-demo.mp4) · [資料說明](DATA-NOTES.txt)

雙圖同步縮放、可調光源，含原始／補值切換。WebGL Horn坡面受光，不是山體投射陰影。影片為32秒實際WebGL自動操作，等比例重新排版、無聲。

## 重現
安裝 GDAL CLI、numpy、scipy、Pillow。執行 `python3 build-fill.py`，由base-data中官方約100m彙整格網及source中Copernicus原始瓦片重建補值GeoTIFF、法向量與遮罩。以 `python3 -m http.server 8000` 開啟 index.html。

完整官方20m原始下載來源及彙整方法見 DATA-NOTES.txt；原始大型ZIP於作者工作目錄保留，未複製進此儲存庫。

資料授權分別依內政部政府資料開放授權條款第1版及Copernicus DEM授權，不以程式授權覆蓋資料授權。來源hash與重疊區檢核見qa.json。缺口內沒有獨立真值，校正樣本誤差不代表缺口內精度。
