import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("logs/analysis_log.jsonl")
LOG_FILE.parent.mkdir(exist_ok=True)


def save_analysis_log(result: dict, source: str = "api"):
    log_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        "input_type": result.get("input_type", "unknown"),
        "decision": result.get("decision", "unknown"),
        "language": result.get("language", "unknown"),
        "confidence": result.get("confidence", None),
        "reasons": result.get("reasons", []),
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")