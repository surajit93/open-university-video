# scripts/upload_youtube.py

import json
import os
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# =========================
# FILES
# =========================

VIDEO_FILE = Path("final.mp4")
SUBTITLE_FILE = Path("final.srt")
THUMBNAIL_FILE = Path("thumbnail.png")
TOPIC_FILE = Path("current_topic.json")
MCQ_LINK_FILE = Path("mcq_link.txt")          # written by publish_mcq.py
CHANNEL_META_FILE = Path("channel.json")      # course / channel metadata

# =========================
# ENV
# =========================

CLIENT_ID = os.environ["YT_CLIENT_ID"]
CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"]
CHANNEL_ID = os.environ["YT_CHANNEL_ID"]

# =========================
# AUTH
# =========================

def get_youtube():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

# =========================
# MAIN
# =========================

def main():
    assert VIDEO_FILE.exists(), "final.mp4 missing"
    assert TOPIC_FILE.exists(), "current_topic.json missing"

    topic = json.loads(TOPIC_FILE.read_text(encoding="utf-8"))

    channel_meta = {}
    if CHANNEL_META_FILE.exists():
        channel_meta = json.loads(CHANNEL_META_FILE.read_text(encoding="utf-8"))

    title = topic["title"]
    base_desc = topic.get("description", title)
    tags = list(set(topic.get("tags", []) + channel_meta.get("default_tags", [])))

    # -------------------------
    # MCQ LINK
    # -------------------------

    mcq_link = ""
    if MCQ_LINK_FILE.exists():
        mcq_link = MCQ_LINK_FILE.read_text(encoding="utf-8").strip()

    # -------------------------
    # DESCRIPTION (ENRICHED)
    # -------------------------

    description = base_desc.strip()

    if mcq_link:
        description += (
            "\n\n📘 Practice Test (MCQs)\n"
            "Test your understanding of this lecture:\n"
            f"{mcq_link}\n\n"
            "⚠️ Note: This practice test is for learning and self-assessment only."
        )

    if "channel_footer" in channel_meta:
        description += "\n\n" + channel_meta["channel_footer"].strip()

    youtube = get_youtube()

    # -------------------------
    # UPLOAD VIDEO
    # -------------------------

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "channelId": CHANNEL_ID,
                "categoryId": "27",  # Education
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(
            VIDEO_FILE,
            mimetype="video/mp4",
            resumable=True
        )
    )

    response = request.execute()
    video_id = response["id"]
    print("✔ Uploaded video:", video_id)

    # -------------------------
    # THUMBNAIL
    # -------------------------

    if THUMBNAIL_FILE.exists():
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(THUMBNAIL_FILE)
        ).execute()
        print("✔ Thumbnail uploaded")

    # -------------------------
    # SUBTITLES
    # -------------------------

    if SUBTITLE_FILE.exists():
        youtube.captions().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "language": "en",
                    "name": "English",
                    "isDraft": False
                }
            },
            media_body=MediaFileUpload(
                SUBTITLE_FILE,
                mimetype="application/octet-stream"
            )
        ).execute()
        print("✔ Subtitles uploaded")

    print("✔ UPLOAD COMPLETE")

if __name__ == "__main__":
    main()
