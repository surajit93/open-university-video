# scripts/pick_topic.py

import json
import sys
from pathlib import Path

TOPICS_FILE = Path("topics.json")
CURRENT_TOPIC_FILE = Path("current_topic.json")


def score_topic(topic):
    """
    Priority scoring system:

    - Higher addiction_score preferred
    - Earlier series_position preferred
    - Must be pending
    """

    addiction = topic.get("addiction_score", 0.5)
    series_position = topic.get("series_position", 999)

    # Higher addiction + earlier series
    return (addiction * 2) - (series_position * 0.01)


def main():
    if not TOPICS_FILE.exists():
        print("ERROR: topics.json not found")
        sys.exit(1)

    with TOPICS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    topics = data.get("topics", [])

    pending_topics = [
        t for t in topics
        if t.get("status") == "pending"
    ]

    if not pending_topics:
        print("No pending topics found. Exiting.")
        sys.exit(0)

    # 🔥 Sort by engineered priority
    pending_topics.sort(key=score_topic, reverse=True)

    selected = pending_topics[0]

    # Mark processing
    for topic in topics:
        if topic["id"] == selected["id"]:
            topic["status"] = "processing"
            break

    CURRENT_TOPIC_FILE.write_text(
        json.dumps(selected, indent=2),
        encoding="utf-8"
    )

    TOPICS_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    print(f"Picked topic (optimized): {selected['id']}")


if __name__ == "__main__":
    main()
