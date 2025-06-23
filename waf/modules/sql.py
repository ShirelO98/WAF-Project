import json
import os
import re

# this function loads SQL rules from a JSON file
def load_sql_rules():
    path = os.path.join(os.path.dirname(__file__), "../rules/sql_rules.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data["rules"]

# function to detect SQL injection patterns in input text
def detect_sqli(input_text):
    rules = load_sql_rules()
    
    for pattern in rules:
        if re.search(pattern, input_text, re.IGNORECASE):
            print(f"[SQLi] Matched rule: {pattern}")
            return True

    return False
