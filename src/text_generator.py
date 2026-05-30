from __future__ import annotations

import json
import os
import random
import re
from typing import List, Optional

import requests

from config import settings
from models import DraftVariant, PostBrief
from prompting import build_text_prompt


def _clean_text(text: str) -> str:
    text = text.strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.replace("```", "")
    return text.strip()


def _truncate_to_limit(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(" ,;:.") + "..."


def _template_generate(brief: PostBrief, seed: int) -> str:
    rng = random.Random(seed)
    openers = [
        f"Most people are reading {brief.topic} the wrong way.",
        f"I keep seeing the same mistake around {brief.topic}.",
        f"This is the part of {brief.topic} most people miss.",
        f"{brief.topic} is more important than it looks.",
        f"If you work in {brief.audience}, this matters now.",
    ]
    angles = [
        f"Here is the practical truth: {brief.belief}.",
        f"The real advantage is not the tool itself. It is the system around it.",
        f"The biggest gap is usually not knowledge. It is workflow design.",
        f"Small implementation choices create big output differences over time.",
    ]
    support = [
        "1) Keep the signal, remove the noise.",
        "2) Reuse what works and discard repetitive patterns.",
        "3) Optimize for outcomes, not vanity metrics.",
    ]
    ctas = [
        "Follow for more practical AI/ML systems.",
        "Check my profile for more breakdowns like this.",
        "What would you improve in this workflow?",
    ]
    body = "\n".join(
        [
            rng.choice(openers),
            "",
            rng.choice(angles),
            "",
            rng.choice(support),
            "2) Use a repeatable process, not a repeated template.",
            "3) Score the output before it goes live.",
            "",
            rng.choice(ctas),
        ]
    )
    return _truncate_to_limit(body, settings.max_post_length)


def _call_gemini(prompt: str) -> Optional[str]:
    key = settings.google_api_key
    if not key:
        return None
    model = settings.text_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.9,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 900,
        },
    }
    r = requests.post(url, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return None
    return _clean_text(parts[0].get("text", ""))


def _call_hf_text(prompt: str) -> Optional[str]:
    token = settings.huggingface_token
    if not token:
        return None
    model = settings.fallback_text_model
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 320,
            "temperature": 0.9,
            "top_p": 0.95,
            "return_full_text": False,
        },
        "options": {"wait_for_model": True},
    }
    r = requests.post(url, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and data:
        text = data[0].get("generated_text", "")
        return _clean_text(text)
    if isinstance(data, dict) and "generated_text" in data:
        return _clean_text(data["generated_text"])
    return None


def generate_post_text(brief: PostBrief, seed: int = 0) -> DraftVariant:
    prompt = build_text_prompt(brief)

    text = None
    if settings.model_provider.lower() == "gemini":
        try:
            text = _call_gemini(prompt)
        except Exception:
            text = None

    if not text and settings.model_provider.lower() in {"hf", "huggingface"}:
        try:
            text = _call_hf_text(prompt)
        except Exception:
            text = None

    if not text:
        text = _template_generate(brief, seed)

    text = _clean_text(text)
    text = _truncate_to_limit(text, settings.max_post_length)
    return DraftVariant(text=text, prompt=prompt)