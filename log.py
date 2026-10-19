import json
import os
from datetime import datetime

LOG_FILE = os.path.join("logs", "assistant.jsonl")

def log_interaction(data: dict):
    """
    Appends an interaction dictionary as a JSON line to the log file.
    """
    os.makedirs("logs", exist_ok=True)
    
    # Add a timestamp if not already present
    if "timestamp" not in data:
        data["timestamp"] = datetime.utcnow().isoformat()
        
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")