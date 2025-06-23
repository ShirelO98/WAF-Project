import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/submissions.json")

def save_submission(submission):  # קולט dict אחד
    try:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        data.append(submission)

        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("[DB] Submission saved successfully.")
    except Exception as e:
        print(f"[DB ERROR] Failed to save submission: {e}")
