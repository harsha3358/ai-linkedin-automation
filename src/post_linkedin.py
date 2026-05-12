import os
import requests

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
PERSON_URN = os.getenv("LINKEDIN_PERSON_URN", "").strip()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0"
}


def register_upload():

    url = "https://api.linkedin.com/v2/assets?action=registerUpload"

    data = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": PERSON_URN,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }

    response = requests.post(
        url,
        headers={
            **HEADERS,
            "Content-Type": "application/json"
        },
        json=data
    )

    response_data = response.json()

    upload_url = response_data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]

    asset = response_data["value"]["asset"]

    return upload_url, asset


def upload_image(upload_url, image_path):

    with open(image_path, "rb") as image:

        response = requests.put(
            upload_url,
            data=image,
            headers={
                "Authorization": f"Bearer {TOKEN}"
            }
        )

    return response.status_code


def create_post(text, asset):

    url = "https://api.linkedin.com/v2/ugcPosts"

    payload = {
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": asset
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(
        url,
        headers={
            **HEADERS,
            "Content-Type": "application/json"
        },
        json=payload
    )

    print("LinkedIn Post Status:", response.status_code)
    print(response.text)


def post_to_linkedin(text, image_path):

    upload_url, asset = register_upload()

    upload_status = upload_image(upload_url, image_path)

    print("Image Upload Status:", upload_status)

    create_post(text, asset)