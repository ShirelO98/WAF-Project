import requests

malicious_files = [
    ("drop.sql", b"DROP TABLE users;"),
    ("evil.php", b"<?php system('rm -rf /'); ?>"),
    ("script.html", b"<script>alert('injected');</script>"),
    ("base64.txt", b"eval(base64_decode('ZWNobyBoZWxsbyE='));")
]

for filename, content in malicious_files:
    print(f"\n[UPLOAD] Uploading: {filename}")
    try:
        files = {
            "file": (filename, content, "text/plain")
        }
        data = {
            "name": "attacker",
            "email": "upload@example.com",
            "message": "upload test"
        }
        res = requests.post("http://localhost:5000/submit", data=data, files=files)
        print(f"> Status: {res.status_code}")
        print(f"> Response: {res.text[:100]}")
    except Exception as e:
        print(f"> Error: {e}")
