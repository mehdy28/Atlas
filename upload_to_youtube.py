import os
import sys
import json

sys.path.append("/content/Atlas")

from config import (
    YOUTUBE_TOKEN_PATH, YOUTUBE_DEFAULT_PRIVACY, YOUTUBE_DEFAULT_CATEGORY,
    FINAL_VIDEO_PATH, SCRIPT_PATH, PRODUCTION_DIR
)
from director.youtube_uploader import get_or_prompt_youtube_token, build_youtube_client, upload_video

if not os.path.exists(FINAL_VIDEO_PATH):
    raise SystemExit("No final video found at " + FINAL_VIDEO_PATH + ". Run the pipeline first.")

title = input("Video title (default: derived from script): ").strip()
if not title:
    title = "Untitled Atlas Video"
    if os.path.exists(SCRIPT_PATH):
        with open(SCRIPT_PATH) as f:
            first_line = f.read().split("\n")[0]
        title = first_line[:80]

description = input("Description (optional, press Enter to skip): ").strip()
if not description and os.path.exists(SCRIPT_PATH):
    with open(SCRIPT_PATH) as f:
        description = f.read()[:1000]

privacy_input = input("Privacy [private/unlisted/public] (default: " + YOUTUBE_DEFAULT_PRIVACY + "): ").strip().lower()
privacy = privacy_input if privacy_input in ("private", "unlisted", "public") else YOUTUBE_DEFAULT_PRIVACY

token_data = get_or_prompt_youtube_token(YOUTUBE_TOKEN_PATH)
youtube = build_youtube_client(token_data)

print("\nUploading " + FINAL_VIDEO_PATH + " as '" + privacy + "'...")
response = upload_video(
    youtube, FINAL_VIDEO_PATH, title, description,
    privacy_status=privacy, category_id=YOUTUBE_DEFAULT_CATEGORY
)

video_id = response.get("id")
print("\nUpload complete!")
print("Video ID: " + str(video_id))
print("URL: https://youtu.be/" + str(video_id))
