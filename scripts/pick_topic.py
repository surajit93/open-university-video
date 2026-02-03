import json
import sys
from pathlib import Path

TOPICS_FILE = Path("topics.json")
CURRENT_TOPIC_FILE = Path("current_topic.json")

def main():
    if not TOPICS_FILE.exists():
        print("ERROR: topics.json not found")
        sys.exit(1)

    with TOPICS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    topics = data.get("topics", [])

    selected = None

    for topic in topics:
        if topic.get("status") == "pending":
            selected = topic
            topic["status"] = "processing"
            break

    if not selected:
        print("No pending topics found. Exiting.")
        sys.exit(0)

    CURRENT_TOPIC_FILE.write_text(
        json.dumps(selected, indent=2),
        encoding="utf-8"
    )

    TOPICS_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print(f"Picked topic: {selected['id']}")

if __name__ == "__main__":
    main()
