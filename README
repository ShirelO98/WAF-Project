# 🛡️ WAF-Project — Web Application Firewall with Machine Learning

A multi-layered Web Application Firewall (WAF) implemented in Python.
Combines **signature-based detection** for known attacks (SQLi, XSS, malicious uploads) with **machine learning–based anomaly detection** to identify stealthy DoS attacks such as Slowloris in real time.

---

## 📚 Overview

This project demonstrates the design and implementation of a lightweight yet extensible WAF system, acting as an inline HTTP proxy.
The system inspects all incoming requests, blocks malicious or anomalous traffic, and logs events for analysis and auditing.

---

## ⚙️ Key Features

### 🔍 Signature-Based Filtering

* Detects known attack patterns using custom regular expressions:

  * **SQL Injection**: payloads like `' OR 1=1 --`, `UNION SELECT`, etc.
  * **Cross-Site Scripting (XSS)**: `<script>`, `onload=`, `javascript:`
  * **Malicious Uploads**: blocks dangerous file extensions like `.php`, `.exe`

### 🤖 Machine Learning Integration

* Utilizes **Isolation Forest** (scikit-learn) to detect anomalous request behavior
* Flags long-lived, slow-drip connections (Slowloris) based on traffic metadata:

  * Packet size, inter-arrival time, header size, duration, etc.
* Enables proactive detection beyond static rules

### 🧪 Attack Simulation Suite

* Includes Python scripts for simulating:

  * SQLi, XSS, file upload attacks
  * Slowloris-style DoS using delayed payload transmission

### 🧵 Multi-threaded Proxy Server

* Built on Python’s `ThreadingHTTPServer` for concurrent connection handling
* Configured with custom timeouts to mitigate DoS without affecting normal clients

### 📝 Logging & Monitoring

* All activity is logged to `waf_log.txt` with clear event tags: `ALLOWED`, `BLOCKED`, `ERROR`
* Useful for debugging, reporting, and future analytics

---

## 🧩 System Architecture

```text
[Client (User/Attacker)]
        │
        ▼
  [WAF Proxy Server]
   ├─ Signature Detection (regex)
   ├─ ML Detection (Isolation Forest)
   └─ Logging (waf_logger)
        │
        ▼
  [Flask Backend Application]
        │
        ▼
  [Local JSON File Store]
```

---

## ▶️ How to Run the Project

This section provides a step-by-step guide to running the WAF system locally.

---

### 📦 Step 1: Install Dependencies

Make sure Python 3.8 or higher is installed. Then, install the required Python packages:

```bash
pip install -r requirements.txt
```

---

### 🛡️ Step 2: Start the WAF Proxy Server

This server filters incoming HTTP requests using both signature-based and ML-based detection.

From the project root:

```bash
py waf/core/proxy.py
```
The proxy server will be available at `http://localhost:5000`

---

### 🔧 Step 3: Launch the Backend Server

This is the simple Flask-based web server that handles clean traffic:

```bash
py server/app/main.py
```

The server will be available at `http://localhost:5001`

---

### 🧠 Step 4 (Optional): Retrain the ML Model

If you want to retrain the anomaly detection model:

```bash
py ml/train/train_model.py
```

This will generate a new `isolation_forest.pkl` file in `ml/model/`.

---

### 🧪 Step 5 (Optional): Run Attack Simulations

You can test the WAF by simulating various attacks:

```bash
cd attacks
py run_all_attacks.py
```

Or run individual attacks:

```bash
py attack_sql.py
py attack_xss.py
py attack_upload.py
py attack_slowloris.py
```

---

### 🌐 Step 6 (Optional): Interact via Client Interface

You can also send normal or malicious requests through the built-in client UI:

```bash
cd client
open index.html  # or double-click the file
```

Use the client interface to:

* Submit regular requests to test allowed behavior
* Craft and send attack payloads (e.g., SQLi, XSS) to observe WAF blocking

---

### 📝 Logs

All activity is saved to `waf/waf_logger/logs/waf_log.txt`, with entries labeled `ALLOWED`, `BLOCKED`, or `ERROR`.
