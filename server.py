import http.server
import os

# المنفذ
PORT = 80

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Welcome to FaceAuthServer</h1>")
        self.wfile.write(b"<p>The server is running on FaceAuthServer.ddns.net</p>")

def run_server():
    server_address = ("0.0.0.0", PORT)
    httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Serving on http://FaceAuthServer.ddns.net:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()