import os
from datetime import datetime

# Path to log file
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_PATH = os.path.join(LOG_DIR, "waf_log.txt")

# Make sure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def log_event(event_type, details):
    """
    Logs WAF events with a timestamp.
    :param event_type: str - 'BLOCKED', 'ALLOWED', 'UPLOAD', etc.
    :param details: str - A description of the event
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{event_type}] {details}\n"

    try:
        with open(LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(entry)
    except Exception as e:
        print(f"[LOGGER ERROR] Could not write to log file: {e}")