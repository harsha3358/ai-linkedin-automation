from __future__ import annotations

import random
import re
from typing import Optional

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


def _template_generate(brief: PostBrief, seed: int, feedback: Optional[str] = None) -> str:
    rng = random.Random(seed)

    context_openers = [
        f"This week, a real-world team could run into {brief.topic} while trying to ship faster without losing quality.",
        f"In practice, {brief.topic} shows up when a team wants better results without adding more compute or manual work.",
        f"A common situation is a product team trying to use {brief.topic} without making the system too complex.",
        f"Many builders hit this problem when they try to apply {brief.topic} in production.",
    ]

    if brief.source_summary:
        context_openers.insert(
            0,
            f"A recent idea around {brief.topic} points to a simple problem: {brief.source_summary[:120].rstrip('.')}."
        )

    hooks = [
        f"Most people miss the real lesson in {brief.topic}.",
        f"The biggest mistake around {brief.topic} is treating it like a buzzword.",
        f"{brief.topic} matters more when you look at the workflow, not the headline.",
        f"Here is the practical truth about {brief.topic}:",
    ]

    explanations = [
        "In simple terms, this is about making a model or system more useful without rebuilding everything from scratch.",
        "In plain English, the idea is to improve the result while keeping the process efficient and manageable.",
        "The technical point is that the system tries to adapt better without adding unnecessary complexity.",
    ]

    why_matters = [
        "That matters because teams care about speed, cost, and quality at the same time.",
        "That matters because better workflows save time and reduce wasted effort.",
        "That matters because a small technical improvement can make the whole system more usable.",
    ]

    examples = [
        "For example, a support team could use this approach to improve answers for a specific domain instead of retraining a full model.",
        "For example, a startup could test this on one workflow before investing in a bigger training pipeline.",
        "For example, an ML team could compare this method with a full retrain and see whether the tradeoff is worth it.",
    ]

    limitations = [
        "The tradeoff is that faster methods can add complexity at inference time or make the system harder to maintain.",
        "The limitation is that not every workflow benefits equally, and the gains can depend on the use case.",
        "The catch is that better efficiency often comes with a more complicated setup.",
    ]

    challenges = [
        "Challenge: look at one AI workflow you use today and ask whether adaptation can replace full retraining.",
        "Challenge: compare two approaches in one workflow and measure which one gives better results for the cost.",
        "Challenge: audit one process today and find one place where you can simplify it without losing quality.",
    ]

    ctas = [
        "Follow for practical AI/ML breakdowns that save time.",
        "Follow for clear AI/ML lessons without the fluff.",
        "Check my profile for more simple, useful AI/ML posts.",
    ]

    body = "\n\n".join(
        [
            rng.choice(hooks),
            rng.choice(context_openers),
            rng.choice(explanations),
            rng.choice(why_matters),
            rng.choice(examples),
            rng.choice(limitations),
            rng.choice(challenges),
            rng.choice(ctas),
        ]
    )

    if feedback:
        body += f"\n\nNote: {feedback}"

    return _truncate_to_limit(_clean_text(body), settings.max_post_length)


def _call_gemini(prompt: str) -> Optional[str]:
    key = settings.google_api_key
    if not key:
        return None

    model = settings.text_model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 700,
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
            "max_new_tokens": 260,
            "temperature": 0.7,
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


def generate_post_text(brief: PostBrief, seed: int = 0, feedback: Optional[str] = None) -> DraftVariant:
    prompt = build_text_prompt(brief, feedback=feedback)

    text = None

    if settings.model_provider.lower() == "gemini":
        try:
            text = _call_gemini(prompt)
        except Exception:
            text = None

    if not text:
        try:
            text = _call_hf_text(prompt)
        except Exception:
            text = None

    if not text:
        text = _template_generate(brief, seed=seed, feedback=feedback)

    text = _clean_text(text)
    text = _truncate_to_limit(text, settings.max_post_length)
    return DraftVariant(text=text, prompt=prompt)