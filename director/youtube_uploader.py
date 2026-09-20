import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_or_prompt_youtube_token(token_path):
    """
    Loads a saved refresh token if present. Otherwise walks the person
    through uploading the one-time-setup JSON file (generated on their
    PC via the OAuth flow, not inside Colab).
    """
    if os.path.exists(token_path):
        with open(token_path) as f:
            data = json.load(f)
        print("Found saved YouTube credentials.")
        return data

    print("\nNo YouTube credentials found.")
    print("Upload the youtube_refresh_token.json file you generated on your PC (see setup instructions).")
    from google.colab import files
    uploaded = files.upload()
    fname = list(uploaded.keys())[0]

    with open(token_path, "wb") as f:
        f.write(uploaded[fname])

    with open(token_path) as f:
        data = json.load(f)

    print("Saved to " + token_path + " - will be reused automatically next time.")
    return data

def build_youtube_client(token_data):
    creds = Credentials(
        token=None,
        refresh_token=token_data["refresh_token"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        token_uri=token_data["token_uri"],
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, video_path, title, description, tags=None,
                  privacy_status="private", category_id="27"):
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or [],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Upload progress: " + str(int(status.progress() * 100)) + "%")

    return response
