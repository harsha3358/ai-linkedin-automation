from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import requests

from config import settings
from models import PostBrief
from prompting import build_image_prompt


def _safe_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:80] or "image"


def _hf_generate_image(prompt: str, out_path: Path) -> Optional[str]:
    token = settings.huggingface_token

    if not token:
        return None

    url = f"https://api-inference.huggingface.co/models/{settings.image_model}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "image/png",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": prompt},
            timeout=45,
        )

        if response.status_code >= 400:
            print("HF image generation failed:", response.status_code)
            return None

        if not response.content:
            return None

        out_path.write_bytes(response.content)

        return str(out_path)

    except Exception as exc:
        print("HF image error:", exc)
        return None


def generate_image(
    brief: PostBrief,
    text: str,
    out_dir: Path,
    seed_tag: str,
    feedback: Optional[str] = None,
) -> Optional[str]:

    out_dir.mkdir(parents=True, exist_ok=True)

    safe = _safe_name(
        f"{brief.topic}_{brief.audience}_{seed_tag}"
    )

    out_path = out_dir / f"{safe}.png"

    prompt = build_image_prompt(
        brief,
        text,
        feedback=feedback,
    )

    return _hf_generate_image(
        prompt,
        out_path,
    )
