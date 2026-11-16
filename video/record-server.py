from http.server import SimpleHTTPRequestHandler,HTTPServer
from pathlib import Path
class H(SimpleHTTPRequestHandler):
 def do_POST(self):
  if self.path!='/recording':self.send_error(404);return
  p=Path('video/day17-demo.webm');p.write_bytes(self.rfile.read(int(self.headers['Content-Length'])));self.send_response(200);self.end_headers();self.wfile.write(b'OK')
HTTPServer(('127.0.0.1',8783),H).serve_forever()
