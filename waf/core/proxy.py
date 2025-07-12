import os
import sys
import re
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote_plus
import requests

# Allow imports from waf/ directory
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from modules import xss, sql, upload
from waf_logger.logger import log_event
from core.slowloris_detector import SlowlorisDetector

# Paths
BASE_DIR    = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
MODEL_PATH  = os.path.join(PROJECT_DIR, "ml", "model", "isolation_forest.pkl")

# Initialize the Slowloris detector
detector = SlowlorisDetector(MODEL_PATH)
BACKEND_URL = "http://localhost:5001"


class WAFHandler(BaseHTTPRequestHandler):
    """WAF handler with CORS, file/XSS/SQLi scanning, Slowloris ML, and proxy."""

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def _safe_block(self, code, msg):
        """Send error code and message, ignoring client disconnects."""
        try:
            self.send_response(code)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(msg)
        except ConnectionResetError:
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        client_ip, client_port = self.client_address

        # 1) Read body with timeout to catch Slowloris
        self.request.settimeout(10)
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
        except (socket.timeout, ConnectionResetError, TimeoutError):
            log_event("BLOCKED", f"Slowloris or broken connection from {client_ip}")
            return self._safe_block(429, b"Blocked: Slowloris attack.\n")

        ct = self.headers.get("Content-Type", "")
        print(f"[WAF] POST {self.path} from {client_ip}, Content-Type: {ct}")

        # 2) File upload scanning
        if "multipart/form-data" in ct:
            fields, fname, fbytes = self.parse_multipart_formdata(raw, ct)
            if fname:
                if upload.is_forbidden_extension(fname):
                    log_event("BLOCKED", f"Ext '{fname}' forbidden from {client_ip}")
                    return self._safe_block(403, b"Blocked: forbidden extension.")
                if fbytes and upload.is_malicious_content(fbytes):
                    log_event("BLOCKED", f"Malicious file '{fname}' from {client_ip}")
                    return self._safe_block(403, b"Blocked: malicious file.")
            for v in fields.values():
                if xss.detect_xss(v) or sql.detect_sqli(v):
                    log_event("BLOCKED", f"XSS/SQLi in field from {client_ip}")
                    return self._safe_block(403, b"Blocked: XSS/SQLi.")
        else:
            decoded = unquote_plus(raw.decode("utf-8", "ignore"))
            if xss.detect_xss(decoded) or sql.detect_sqli(decoded):
                log_event("BLOCKED", f"XSS/SQLi in body from {client_ip}")
                return self._safe_block(403, b"Blocked: XSS/SQLi.")

        # 3) Slowloris ML detection
        key = (client_ip, client_port)
        hdr_bytes = sum(len(k) + len(v) for k, v in self.headers.items())
        detector.record_request(key, hdr_bytes, len(raw))
        if detector.is_slowloris(key):
            log_event("BLOCKED", f"Slowloris detected from {client_ip}")
            return self._safe_block(429, b"Blocked: Slowloris.")

        # 4) Forward to backend
        try:
            resp = requests.post(BACKEND_URL + self.path, data=raw,
                                 headers={"Content-Type": ct})
        except Exception as e:
            log_event("ERROR", f"Backend error: {e}")
            return self._safe_block(500, f"Error: {e}".encode())

        # 5) Relay backend response
        try:
            self.send_response(resp.status_code)
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(resp.content)
            log_event("ALLOWED", f"Forwarded {self.path} from {client_ip}")
        except ConnectionResetError:
            log_event("ERROR", f"Client {client_ip} disconnected early")
        except Exception as e:
            log_event("ERROR", f"Send error to {client_ip}: {e}")

    def parse_multipart_formdata(self, body, ct):
        m = re.search(r"boundary=([-_a-zA-Z0-9]+)", ct)
        if not m:
            return {}, None, None
        b = m.group(1).encode()
        parts = body.split(b"--" + b)
        fields, fn, fb = {}, None, None
        for part in parts:
            if not part or part == b"--\r\n": continue
            h, _, c = part.partition(b"\r\n\r\n")
            c = c.rstrip(b"\r\n")
            if b"filename=" in h:
                m2 = re.search(b'filename="([^"]+)"', h)
                if m2:
                    fn = m2.group(1).decode("utf-8", "ignore")
                    fb = c
            else:
                m2 = re.search(b'name="([^"]+)"', h)
                if m2:
                    fields[m2.group(1).decode()] = c.decode("utf-8", "ignore")
        return fields, fn, fb


def run_proxy():
    server = ThreadingHTTPServer(("localhost", 5000), WAFHandler)
    print("✅ WAF Proxy (multi-threaded) running on http://localhost:5000")
    server.serve_forever()


if __name__ == "__main__":
    run_proxy()
