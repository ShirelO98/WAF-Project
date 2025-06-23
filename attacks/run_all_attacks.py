import subprocess
from colorama import Fore, Style, init
import os

init(autoreset=True)

# נתיב אבסולוטי לקובץ זה (run_all_attacks.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# קבצי ההתקפות
files = ["attack_sql.py", "attack_xss.py", "attack_upload.py"]

# קובץ לוג
log_file_path = os.path.join(BASE_DIR, "attack_log.txt")

print(Fore.CYAN + "🚀 Running all attack simulations...\n")

with open(log_file_path, "w", encoding="utf-8") as log_file:
    for file in files:
        full_path = os.path.join(BASE_DIR, file)
        header = f"=== Running: {file} ===\n"
        print(Fore.YELLOW + header)
        log_file.write(header)

        process = subprocess.Popen(
            ["python", full_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(Fore.WHITE + line.strip())
            log_file.write(line)

        log_file.write("\n")

print(Fore.GREEN + f"\n✅ All attacks completed. Log saved to: {log_file_path}")
