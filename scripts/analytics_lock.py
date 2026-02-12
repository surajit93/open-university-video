import datetime

ALLOWED_WEEKDAY = "Sunday"

def analytics_access_allowed():
    today = datetime.datetime.now()
    if today.strftime("%A") == ALLOWED_WEEKDAY:
        return True
    return False

def enforce_analytics_lock():
    if not analytics_access_allowed():
        raise Exception("Analytics locked. Weekly review only.")
    print("Analytics access granted (weekly window).")
