from __future__ import annotations

import math
import re
from functools import lru_cache
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

from config import settings
from models import DraftVariant, PostBrief, TrendItem
from storage import normalize_text, recent_texts, text_signature, load_history


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _pct(x: float) -> float:
    return _clamp(x * 100.0, 0.0, 100.0)


def _has_number(text: str) -> bool:
    return bool(re.search(r"\d", text))


def _contains_cta(text: str) -> bool:
    cta_words = ["follow", "profile", "check my profile", "save", "share", "comment", "tell me", "what would you"]
    t = text.lower()
    return any(w in t for w in cta_words)


def _first_line(text: str) -> str:
    return text.strip().splitlines()[0] if text.strip() else ""


def _hook_strength(text: str) -> float:
    first = _first_line(text)
    score = 0.0
    if len(first) <= 180:
        score += 25
    if "?" in first:
        score += 18
    if any(x in first.lower() for x in ["wrong", "mistake", "miss", "nobody", "most people", "actually", "shouldn't"]):
        score += 25
    if _has_number(first):
        score += 10
    if len(first.split()) <= 14:
        score += 12
    if first and first[0].isupper():
        score += 10
    return _clamp(score)


def _clarity_score(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    avg_len = sum(len(w) for w in words) / len(words)
    score = 100.0
    if avg_len > 7:
        score -= min(25, (avg_len - 7) * 5)
    if len(words) > settings.max_post_length:
        score -= min(20, (len(words) - settings.max_post_length) * 0.5)
    sentence_count = max(1, len(re.split(r"[.!?]+", text)) - 1)
    if sentence_count < 3:
        score -= 10
    if sentence_count > 8:
        score -= 5
    return _clamp(score)


def _utility_score(text: str, brief: PostBrief) -> float:
    t = text.lower()
    score = 0.0
    if any(word in t for word in ["workflow", "system", "process", "steps", "checklist", "framework"]):
        score += 25
    if any(word in t for word in ["practical", "implement", "build", "ship", "useful"]):
        score += 20
    if brief.audience in t:
        score += 10
    if _has_number(text):
        score += 10
    if len(text.split()) >= 60:
        score += 10
    if _contains_cta(text):
        score += 10
    return _clamp(score)


def _novelty_score(text: str, history: Dict) -> float:
    recent = recent_texts(history, limit=settings.recent_post_limit)
    if not recent:
        return 100.0
    best = 0.0
    for prev in recent[-25:]:
        ratio = SequenceMatcher(None, normalize_text(text), normalize_text(prev)).ratio()
        best = max(best, ratio)
    novelty = (1.0 - best) * 100.0
    return _clamp(novelty)


def _audience_score(text: str, brief: PostBrief) -> float:
    t = text.lower()
    audience_markers = {
        "students": ["student", "learn", "career", "portfolio", "internship"],
        "ai engineers": ["agent", "llm", "inference", "prompt", "pipeline", "model"],
        "ml engineers": ["training", "data", "deployment", "latency", "evaluation", "feature"],
        "founders": ["business", "revenue", "product", "market", "opportunity", "customer"],
        "recruiters": ["hiring", "candidate", "skills", "resume", "profile"],
        "ctos": ["strategy", "adoption", "risk", "architecture", "production"],
        "job seekers": ["job", "interview", "role", "portfolio", "skills"],
        "developers": ["build", "code", "ship", "debug", "workflow"],
    }
    markers = audience_markers.get(brief.audience, [])
    hits = sum(1 for m in markers if m in t)
    score = 20 + hits * 16
    return _clamp(score)


@lru_cache(maxsize=1)
def _load_clip():
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
    except Exception:
        return None

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return model, processor, device


def clip_similarity(text: str, image_path: str) -> float:
    pack = _load_clip()
    if pack is None:
        return 0.0
    model, processor, device = pack
    try:
        import torch
        image = Image.open(image_path).convert("RGB")
        inputs = processor(text=[text], images=image, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            img = outputs.image_embeds
            txt = outputs.text_embeds
            img = img / img.norm(dim=-1, keepdim=True)
            txt = txt / txt.norm(dim=-1, keepdim=True)
            sim = (img @ txt.T).squeeze().item()
            return float((_clamp(((sim + 1.0) / 2.0) * 100.0)))
    except Exception:
        return 0.0


def _profile_visit_probability(text: str, brief: PostBrief, novelty: float, audience: float, hook: float, utility: float, cta: float) -> float:
    score = (
        0.22 * novelty
        + 0.20 * hook
        + 0.18 * audience
        + 0.18 * utility
        + 0.12 * cta
        + 0.10 * (100.0 if brief.belief else 0.0)
    )
    return _clamp(score)


def _follow_probability(text: str, brief: PostBrief, profile_visit: float, utility: float, novelty: float) -> float:
    score = 0.45 * profile_visit + 0.25 * utility + 0.20 * novelty + 0.10 * (100.0 if _contains_cta(text) else 0.0)
    return _clamp(score)


def _save_probability(text: str, utility: float, clarity: float, novelty: float) -> float:
    score = 0.40 * utility + 0.30 * clarity + 0.30 * novelty
    return _clamp(score)


def _share_probability(text: str, hook: float, novelty: float, clarity: float) -> float:
    score = 0.40 * hook + 0.35 * novelty + 0.25 * clarity
    return _clamp(score)


def _comment_probability(text: str, hook: float, audience: float) -> float:
    score = 0.60 * hook + 0.40 * audience
    if "?" in text:
        score += 5
    return _clamp(score)


def score_text(text: str, brief: PostBrief, history: Dict) -> Dict[str, float]:
    hook = _hook_strength(text)
    clarity = _clarity_score(text)
    utility = _utility_score(text, brief)
    novelty = _novelty_score(text, history)
    audience = _audience_score(text, brief)
    cta = 100.0 if _contains_cta(text) else 30.0

    text_quality = (
        0.22 * hook
        + 0.20 * clarity
        + 0.24 * utility
        + 0.18 * novelty
        + 0.08 * audience
        + 0.08 * cta
    )

    profile_visit_probability = _profile_visit_probability(text, brief, novelty, audience, hook, utility, cta)
    follow_probability = _follow_probability(text, brief, profile_visit_probability, utility, novelty)
    save_probability = _save_probability(text, utility, clarity, novelty)
    share_probability = _share_probability(text, hook, novelty, clarity)
    comment_probability = _comment_probability(text, hook, audience)

    follower_score = (
        settings.follower_score_weights["profile_visit_probability"] * profile_visit_probability
        + settings.follower_score_weights["follow_probability"] * follow_probability
        + settings.follower_score_weights["save_probability"] * save_probability
        + settings.follower_score_weights["share_probability"] * share_probability
        + settings.follower_score_weights["comment_probability"] * comment_probability
    )

    return {
        "text_quality": _clamp(text_quality),
        "hook_strength": hook,
        "clarity": clarity,
        "utility": utility,
        "novelty": novelty,
        "audience_match": audience,
        "cta_strength": cta,
        "profile_visit_probability": profile_visit_probability,
        "follow_probability": follow_probability,
        "save_probability": save_probability,
        "share_probability": share_probability,
        "comment_probability": comment_probability,
        "follower_score": _clamp(follower_score),
    }


def score_trend_item(item: TrendItem) -> float:
    title = item.title.lower()
    summary = (item.summary or "").lower()
    score = 0.0

    if any(x in title for x in ["llm", "ai", "machine learning", "generative", "agent", "openai", "anthropic", "gemini", "claude"]):
        score += 30
    if any(x in summary for x in ["released", "paper", "workflow", "benchmark", "guide", "tutorial", "analysis"]):
        score += 20
    if any(x in title for x in ["benchmark", "paper", "release", "update", "launch"]):
        score += 10
    if item.source.startswith("arxiv"):
        score += 15
    if item.source.startswith("hackernews"):
        score += 10
    if item.source.startswith("reddit"):
        score += 8
    if item.source.startswith("github"):
        score += 12

    title_tokens = len(set(re.findall(r"[a-zA-Z]{4,}", title)))
    score += min(15, title_tokens * 1.5)

    if "?" in title:
        score += 5

    return _clamp(score)


    def score_candidate(text: str, image_path: str, brief: PostBrief, history: Dict) -> Dict[str, float]:
        text_scores = score_text(text, brief, history)
        clip = (
        clip_similarity(
            brief.topic[:70],
            image_path
        )
        if image_path
        else 0.0
    )

    final = (
        settings.score_weights["text_quality"] * text_scores["text_quality"]
        + settings.score_weights["hook_strength"] * text_scores["hook_strength"]
        + settings.score_weights["audience_match"] * text_scores["audience_match"]
        + settings.score_weights["novelty"] * text_scores["novelty"]
        + settings.score_weights["clarity"] * text_scores["clarity"]
        + settings.score_weights["utility"] * text_scores["utility"]
        + settings.score_weights["cta_strength"] * text_scores["cta_strength"]
        + settings.score_weights["clip"] * clip
    )

    repetition = 0.0
    recent = recent_texts(history, limit=settings.recent_post_limit)
    if recent:
        repetition = max(SequenceMatcher(None, normalize_text(text), normalize_text(prev)).ratio() for prev in recent[-25:]) * 100.0

    publish_ready = (
        final >= settings.publish_threshold
        and text_scores["follower_score"] >= settings.min_follow_probability
        and text_scores["profile_visit_probability"] >= settings.min_profile_visit_probability
        and clip >= settings.clip_threshold * 100.0
        and repetition <= settings.max_repetition_similarity * 100.0
    )

    return {
        **text_scores,
        "clip": clip,
        "final_score": _clamp(final),
        "repetition_similarity": repetition,
        "publish_ready": 1.0 if publish_ready else 0.0,
    }
