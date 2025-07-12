from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from urllib.parse import unquote_plus
import re
import os
import sys

# Add parent directory to sys.path to allow module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules import xss, sql, upload
from waf_logger.logger import log_event 

BACKEND_URL = "http://localhost:5001"

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
        raw_body = self.rfile.read(content_length)
        content_type = self.headers.get("Content-Type", "")

        print(f"\n[WAF] Received POST to {self.path}")
        print(f"[WAF] Content-Type: {content_type}")

        client_ip = self.client_address[0]

        if "multipart/form-data" in content_type:
            fields, filename, file_bytes = self.parse_multipart_formdata(raw_body, content_type)

            if filename:
                print(f"[WAF] Uploaded file: {filename}")
                if upload.is_forbidden_extension(filename):
                    log_event("BLOCKED", f"Forbidden file extension '{filename}' from IP {client_ip}")
                    self._block(403, b"Blocked by WAF: forbidden file type.")
                    return
                if file_bytes and upload.is_malicious_content(file_bytes):
                    log_event("BLOCKED", f"Malicious file content in '{filename}' from IP {client_ip}")
                    self._block(403, b"Blocked by WAF: malicious file content.")
                    return

            for field_val in fields.values():
                if xss.detect_xss(field_val):
                    log_event("BLOCKED", f"XSS detected in form field from IP {client_ip}: {field_val}")
                    self._block(403, b"Blocked by WAF: XSS or SQLi detected.")
                    return
                if sql.detect_sqli(field_val):
                    log_event("BLOCKED", f"SQL Injection detected in form field from IP {client_ip}: {field_val}")
                    self._block(403, b"Blocked by WAF: XSS or SQLi detected.")
                    return

        else:
            decoded_body = unquote_plus(raw_body.decode('utf-8', errors='ignore'))
            print(f"[WAF] Decoded Body: {decoded_body}")

            if xss.detect_xss(decoded_body):
                log_event("BLOCKED", f"XSS detected in body from IP {client_ip}: {decoded_body}")
                self._block(403, b"Blocked by WAF: suspected XSS attack.")
                return

            if sql.detect_sqli(decoded_body):
                log_event("BLOCKED", f"SQL Injection detected in body from IP {client_ip}: {decoded_body}")
                self._block(403, b"Blocked by WAF: suspected SQL Injection.")
                return

        try:
            response = requests.post(
                BACKEND_URL + self.path,
                data=raw_body,
                headers={"Content-Type": content_type}
            )
            log_event("ALLOWED", f"Request to {self.path} forwarded to backend from IP {client_ip}")
            self.send_response(response.status_code)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(response.content)

        except Exception as e:
            log_event("ERROR", f"Failed to contact backend: {e}")
            self._block(500, f"Error contacting backend: {e}".encode())

    def _block(self, status_code, message_bytes):
        self.send_response(status_code)
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(message_bytes)

    def parse_multipart_formdata(self, body_bytes, content_type):
        match = re.search(r'boundary=([-_a-zA-Z0-9]+)', content_type)
        if not match:
            return {}, None, None

        boundary = match.group(1).encode()
        parts = body_bytes.split(b"--" + boundary)

        fields = {}
        filename = None
        file_bytes = None

        for part in parts:
            if not part or part == b'--\r\n':
                continue

            headers, _, content = part.partition(b'\r\n\r\n')
            content = content.rstrip(b'\r\n')

            if b'filename=' in headers:
                match = re.search(b'filename="([^"]+)"', headers)
                if match:
                    filename = match.group(1).decode('utf-8', errors='ignore')
                    file_bytes = content
            else:
                match = re.search(b'name="([^"]+)"', headers)
                if match:
                    field_name = match.group(1).decode('utf-8', errors='ignore')
                    fields[field_name] = content.decode('utf-8', errors='ignore')

        return fields, filename, file_bytes

def run_proxy():
    server = HTTPServer(('localhost', 5000), WAFHandler)
    print("✅ Smart WAF Proxy is running at http://localhost:5000")
    server.serve_forever()

if __name__ == "__main__":
    run_proxy()
