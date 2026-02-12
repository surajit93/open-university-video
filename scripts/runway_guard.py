import json
from pathlib import Path

UPLOAD_LOG = Path("data/upload_history.json")

def get_upload_count():
    if not UPLOAD_LOG.exists():
        return 0
    data = json.loads(UPLOAD_LOG.read_text())
    return len(data)

def check_runway(growth_plan):
    upload_count = get_upload_count()
    threshold = growth_plan["no_major_pivot_before"]

    if upload_count < threshold:
        print("Runway active: Major pivots disabled.")
        return False

    print("Runway completed: Strategic pivots allowed.")
    return True
