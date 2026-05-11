import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "Content-Type": "application/json"
}

def post_to_linkedin(text):

    post_data = {
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=post_data
    )

    print("STATUS:", response.status_code)
    print(response.text)