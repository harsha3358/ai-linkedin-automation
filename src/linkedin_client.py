from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests

from config import settings
from models import PublishResult


LINKEDIN_API = "https://api.linkedin.com/v2"


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }


def get_member_urn(access_token: str) -> str:
    r = requests.get(f"{LINKEDIN_API}/me", headers=_headers(access_token), timeout=30)
    r.raise_for_status()
    data = r.json()
    return f"urn:li:person:{data['id']}"


def register_image_upload(access_token: str, author_urn: str) -> Tuple[str, str]:
    payload = {
        "registerUploadRequest": {
            "owner": author_urn,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [
                {
                    "identifier": "urn:li:userGeneratedContent",
                    "relationshipType": "OWNER",
                }
            ],
        }
    }
    r = requests.post(
        f"{LINKEDIN_API}/assets?action=registerUpload",
        headers=_headers(access_token),
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    value = data["value"]
    asset = value["asset"]
    upload_mechanism = value["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]
    upload_url = upload_mechanism["uploadUrl"]
    return asset, upload_url


def upload_image(upload_url: str, image_path: str) -> None:
    content = Path(image_path).read_bytes()
    r = requests.put(
        upload_url,
        data=content,
        headers={"Content-Type": "application/octet-stream"},
        timeout=120,
    )
    r.raise_for_status()


def create_ugc_post(access_token: str, author_urn: str, text: str, asset_urn: Optional[str] = None) -> PublishResult:
    if asset_urn:
        media_category = "IMAGE"
        media = [
            {
                "status": "READY",
                "description": {"text": "LinkedIn post image"},
                "media": asset_urn,
                "title": {"text": "AI/ML post visual"},
            }
        ]
    else:
        media_category = "NONE"
        media = []

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": media_category,
                "media": media,
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    r = requests.post(
        f"{LINKEDIN_API}/ugcPosts",
        headers=_headers(access_token),
        json=payload,
        timeout=60,
    )

    if r.status_code not in (200, 201):
        return PublishResult(
            published=False,
            status_code=r.status_code,
            response_text=r.text,
            error="LinkedIn post failed",
        )

    post_urn = ""
    try:
        post_urn = r.headers.get("x-restli-id", "") or r.json().get("id", "")
    except Exception:
        pass

    return PublishResult(
        published=True,
        status_code=r.status_code,
        response_text=r.text,
        post_urn=post_urn,
        asset_urn=asset_urn or "",
    )


def post_to_linkedin(text: str, image_path: Optional[str] = None) -> PublishResult:
    token = settings.linkedin_access_token
    if not token:
        return PublishResult(published=False, error="Missing LINKEDIN_ACCESS_TOKEN")

    author_urn = settings.linkedin_person_urn
    if not author_urn:
        try:
            author_urn = get_member_urn(token)
        except Exception as exc:
            return PublishResult(published=False, error=f"Could not resolve LinkedIn URN: {exc}")

    asset_urn = ""
    if image_path:
        try:
            asset_urn, upload_url = register_image_upload(token, author_urn)
            upload_image(upload_url, image_path)
        except Exception as exc:
            return PublishResult(published=False, error=f"Image upload failed: {exc}")

    try:
        return create_ugc_post(token, author_urn, text, asset_urn if asset_urn else None)
    except Exception as exc:
        return PublishResult(published=False, error=str(exc))