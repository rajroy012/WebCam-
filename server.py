from http.server import BaseHTTPRequestHandler, HTTPServer
import json, base64, os, time, urllib.parse

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

data_store = {}

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/":
            self.serve("index.html")

        elif path.startswith("/cam/"):
            self.serve("cam.html")

        elif path == "/data":
            self.send_json(data_store)

        elif path.startswith("/uploads/"):
            try:
                with open(path[1:], "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()
                    self.wfile.write(f.read())
            except:
                self.send_error(404)

        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/upload":
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))

            code = data["code"]
            img_data = base64.b64decode(data["image"].split(",")[1])

            filename = f"{UPLOAD_DIR}/{code}_{int(time.time())}.png"
            with open(filename, "wb") as f:
                f.write(img_data)

            data_store.setdefault(code, []).append(filename)

            self.send_response(200)
            self.end_headers()

    def serve(self, file):
        with open(file, "rb") as f:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read())

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# Render compatible PORT
import os
PORT = int(os.environ.get("PORT", 8080))

print("Server running...")
HTTPServer(("", PORT), Handler).serve_forever()
