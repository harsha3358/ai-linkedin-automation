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

    model = settings.image_model
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "image/png",
    }
    payload = {"inputs": prompt}

    r = requests.post(url, headers=headers, json=payload, timeout=180)
    if r.status_code >= 400 or not r.content:
        return None

    content_type = r.headers.get("content-type", "").lower()
    if "image" not in content_type and r.content[:4] != b"\x89PNG":
        return None

    out_path.write_bytes(r.content)
    return str(out_path)


def _local_generate_image(prompt: str, out_path: Path) -> Optional[str]:
    try:
        import torch
        from diffusers import AutoPipelineForText2Image, StableDiffusionXLPipeline
    except Exception:
        return None

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    pipeline = None
    for model_id in [settings.image_model, settings.fallback_image_model]:
        try:
            pipeline = AutoPipelineForText2Image.from_pretrained(model_id, torch_dtype=dtype)
            pipeline = pipeline.to(device)
            break
        except Exception:
            try:
                pipeline = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
                pipeline = pipeline.to(device)
                break
            except Exception:
                pipeline = None

    if pipeline is None:
        return None

    try:
        image = pipeline(
            prompt=prompt,
            num_inference_steps=20 if device == "cuda" else 10,
            guidance_scale=4.0,
        ).images[0]
        image.save(out_path)
        return str(out_path)
    except Exception:
        return None


def generate_image(
    brief: PostBrief,
    text: str,
    out_dir: Path,
    seed_tag: str,
    feedback: Optional[str] = None,
) -> Optional[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = _safe_name(f"{brief.topic}_{brief.audience}_{seed_tag}")
    out_path = out_dir / f"{safe}.png"
    prompt = build_image_prompt(brief, text, feedback=feedback)

    if settings.image_provider.lower() in {"hf", "huggingface"}:
        try:
            result = _hf_generate_image(prompt, out_path)
            if result:
                return result
        except Exception:
            pass

    try:
        result = _local_generate_image(prompt, out_path)
        if result:
            return result
    except Exception:
        pass

    return None