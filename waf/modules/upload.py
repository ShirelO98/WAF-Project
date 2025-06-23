import os

# Dangerous file extensions (by filename)
FORBIDDEN_EXTENSIONS = [
    '.exe', '.php', '.sh', '.js', '.bat', '.vbs'
]

# Dangerous content patterns (by file content)
FORBIDDEN_CONTENT_KEYWORDS = [
    "malicious",
    "eval(",
    "base64_decode(",
    "<script>",
    "DROP TABLE",
    "<?php",  # start of PHP code
    "<iframe"
]

# Check if the uploaded file has a forbidden extension
def is_forbidden_extension(filename):
    _, ext = os.path.splitext(filename)
    if ext.lower() in FORBIDDEN_EXTENSIONS:
        print(f"[UPLOAD] Forbidden file extension detected: {ext}")
        return True
    return False

# Check if the uploaded file contains forbidden keywords in its content
def is_malicious_content(file_bytes):
    try:
        # Decode file content (ignore non-text chars)
        content = file_bytes.decode("utf-8", errors="ignore")
        print(f"[DEBUG] Decoded file content: {content[:100]}")  # Only first 100 chars for preview

        for keyword in FORBIDDEN_CONTENT_KEYWORDS:
            if keyword.lower() in content.lower():
                print(f"[UPLOAD] Forbidden content found: {keyword}")
                return True

    except Exception as e:
        print(f"[UPLOAD] Error reading file content: {e}")

    return False
