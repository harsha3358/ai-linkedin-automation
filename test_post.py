import requests

TOKEN = "AQW4jpYq4kLfPxJcrSSL9wKkSFVA0CDz_nt6tWsZzM_TcAnQyD7b9NI_Q8Ufn96yUzihuXj_SVL7mf_rQw8CWFHXW__GoEUHn5h4NXVCk62xZNdyAi6dh9N1rkyseFNj0wMKRFL3_hsAfU7i0aAAwdXOQKXt-ODbq4lMjhnsVQ0uEczfmLob5CuoXYYG1GZM9Xy_4gK4MKzrDlFH4UOaO6uVffNRdOozcq2mhPuvefVEimrQxegSeIzOzv-S-8axh0yJa-XdDdE4NjivS1HAU68_P8V_zvnFfrNvZ_XkNoDT19SYd1x87PpNckTgU6k68qzkVGA9ri4wtOD7HMbs77_pJvXscg"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-Restli-Protocol-Version": "2.0.0",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.linkedin.com/v2/ugcPosts",
    headers=headers,
    json={
        "author": "urn:li:person:YOUR_PERSON_URN",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Test post from AI automation 🚀"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
)

print(response.text)