import datetime

def enforce_cadence(channel_config):
    today = datetime.datetime.now()

    allowed_days = channel_config["upload_days"]
    upload_time = channel_config["upload_time"]

    if today.strftime("%A") not in allowed_days:
        raise Exception("Upload blocked: Not scheduled upload day")

    scheduled_hour = int(upload_time.split(":")[0])

    if today.hour < scheduled_hour:
        raise Exception("Upload blocked: Too early")

    print("Cadence validated.")
