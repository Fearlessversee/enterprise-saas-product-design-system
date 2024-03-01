import http.server
import os
import json
import urllib.parse
import mimetypes
import functools
import sys

PORT = 5177
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("audio/mpeg", ".mp3")
mimetypes.add_type("audio/wav", ".wav")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("application/octet-stream", ".riv")

class CleanEnterpriseHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        clean_path = parsed.path.rstrip('/')
        if clean_path.startswith('/api'):
            length = int(self.headers.get('Content-Length', 0))
            if length > 0:
                self.rfile.read(length)
            resp_bytes = b'{"success": true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        clean_path = path.rstrip('/')

        # 1. DevTools & Meta Probes
        if clean_path in ('/meta.json', '/.well-known/appspecific/com.chrome.devtools.json'):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")
            return

        # 2. Dynamic subpage routing
        rel_path = clean_path.lstrip('/')
        if rel_path:
            target_dir = os.path.join(DIRECTORY, rel_path.replace('/', os.sep))
            if os.path.isdir(target_dir):
                target_index = os.path.join(target_dir, "index.html")
                if os.path.exists(target_index):
                    self.path = f"/{rel_path}/index.html"

        super().do_GET()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    handler = functools.partial(CleanEnterpriseHandler, directory=DIRECTORY)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    print("=" * 60)
    print(f" Enterprise Product Design Portal Live: http://localhost:{PORT}")
    print(f" Directory: {DIRECTORY}")
    print("=" * 60)
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
