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
        topics = json.load(f)

    selected = None

    for topic in topics:
        if topic.get("status") == "pending":
            selected = topic
            topic["status"] = "processing"
            break

    if not selected:
        print("No pending topics found. Exiting.")
        sys.exit(0)

    # Write current topic for downstream steps
    with CURRENT_TOPIC_FILE.open("w", encoding="utf-8") as f:
        json.dump(selected, f, indent=2)

    # Persist updated topics.json
    with TOPICS_FILE.open("w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)

    print(f"Picked topic: {selected['id']}")

if __name__ == "__main__":
    main()

