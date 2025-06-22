from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import re
from urllib.parse import unquote_plus

# the URL of the backend service to forward requests to
BACKEND_URL = "http://localhost:5001"

# to check if the decoded body contains malicious content
def is_malicious(decoded_body):
    return bool(re.search(r"<script.*?>", decoded_body, re.IGNORECASE))

class WAFHandler(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8')
        decoded_body = unquote_plus(raw_body)  # מפענחים לפני בדיקת XSS

        print(f"\n[WAF] Received POST to {self.path}")
        print(f"RAW Body: {raw_body}")
        print(f"Decoded Body: {decoded_body}")

        if is_malicious(decoded_body):
            self.send_response(403)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(b"Blocked by WAF: suspected XSS attack.")
            print("[WAF] Blocked request due to suspicious content.\n")
            return

        # if the body is clean, forward the request to the backend
        try:
            response = requests.post(
                BACKEND_URL + self.path,
                data=raw_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            self.send_response(response.status_code)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(response.content)

        except Exception as e:
            self.send_response(500)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(f"Error contacting backend: {e}".encode())

def run_proxy():
    server = HTTPServer(('localhost', 5000), WAFHandler)
    print("✅ WAF proxy is running on http://localhost:5000")
    server.serve_forever()

if __name__ == "__main__":
    run_proxy()
