from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

from config import settings
from models import PostBrief
from prompting import build_image_prompt


def _safe_name(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:80] or "image"


def _create_fallback_image(out_path: Path):
    img = Image.new("RGB", (1024, 1024), color=(20, 20, 20))
    img.save(out_path)
    return str(out_path)


def _hf_generate_image(prompt: str, out_path: Path) -> Optional[str]:

    token = settings.huggingface_token

    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = (
        f"https://api-inference.huggingface.co/models/"
        f"{settings.image_model}"
    )

    try:

        response = requests.post(
            url,
            headers=headers,
            json={"inputs": prompt},
            timeout=180
        )

        if response.status_code == 200:

            out_path.write_bytes(response.content)

            return str(out_path)

    except Exception:
        pass

    return None


def generate_image(
    brief: PostBrief,
    text: str,
    out_dir: Path,
    seed_tag: str
) -> Optional[str]:

    out_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_name = _safe_name(
        f"{brief.topic}_{brief.audience}_{seed_tag}"
    )

    out_path = out_dir / f"{safe_name}.png"

    prompt = build_image_prompt(
        brief,
        text
    )

    image_path = _hf_generate_image(
        prompt,
        out_path
    )

    if image_path:
        return image_path

    return _create_fallback_image(out_path)