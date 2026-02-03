import json
import sys
from pathlib import Path

TOPICS_FILE = Path("topics.json")
CURRENT_TOPIC_FILE = Path("current_topic.json")

def main():
    if not TOPICS_FILE.exists() or not CURRENT_TOPIC_FILE.exists():
        print("ERROR: required files missing")
        sys.exit(1)

    data = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    topics = data.get("topics", [])

    current = json.loads(CURRENT_TOPIC_FILE.read_text(encoding="utf-8"))
    current_id = current["id"]

    found = False

    for topic in topics:
        if topic["id"] == current_id:
            topic["status"] = "done"
            found = True
            break

    if not found:
        print(f"WARNING: topic {current_id} not found")

    TOPICS_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print(f"Marked topic done: {current_id}")

if __name__ == "__main__":
    main()
