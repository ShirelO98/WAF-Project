from flask import Blueprint, request, jsonify
from fake_db import save_submission
import os

app = Blueprint("routes", __name__)

# Define the upload folder for files
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../db/files"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/submit", methods=["POST"])
def handle_submission():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    # Check for uploaded file
    uploaded_file = request.files.get('file')
    saved_filename = None

    if uploaded_file:
        saved_filename = uploaded_file.filename
        save_path = os.path.join(UPLOAD_FOLDER, saved_filename)
        uploaded_file.save(save_path)
        print(f"[SERVER] Saved uploaded file to: {save_path}")

    # Build submission record
    submission = {
        "name": name,
        "email": email,
        "message": message,
        "uploaded_file": saved_filename
    }

    save_submission(submission)
    return jsonify({"status": "success", "message": "Submission received"}), 200
