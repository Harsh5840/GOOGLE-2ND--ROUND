# packages/utils/logger.py

from datetime import datetime

def log_event(source: str, message: str):
    print(f"[{datetime.now().isoformat()}] [{source}] {message}")
