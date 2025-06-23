import json
import os
import re

# this function loads XSS rules from a JSON file
def load_xss_rules():
    path = os.path.join(os.path.dirname(__file__), "../rules/xss_rules.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data["rules"]

# function to detect XSS patterns in input text
def detect_xss(input_text):
    rules = load_xss_rules()

    for pattern in rules:
        if re.search(pattern, input_text, re.IGNORECASE):
            print(f"[XSS] Matched rule: {pattern}")
            return True

    return False
