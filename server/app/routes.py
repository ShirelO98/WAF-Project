from flask import Blueprint, request
from fake_db import save_submission  # שימי לב שהשמטנו את 'app.'
import json

app = Blueprint("routes", __name__)

@app.route("/submit", methods=["POST"])
def handle_submission():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    submission = {
        "name": name,
        "email": email,
        "message": message
    }

    save_submission(submission)
    return json.dumps({"status": "success", "message": "Submission received"}), 200
