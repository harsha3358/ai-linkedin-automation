from __future__ import annotations

import re
from functools import lru_cache
from difflib import SequenceMatcher
from typing import Dict, Optional

import numpy as np
from PIL import Image

from config import settings
from models import PostBrief, TrendItem
from storage import normalize_text, recent_texts


REAL_WORLD_MARKERS = [
    "this week",
    "real-world",
    "in practice",
    "imagine",
    "when a team",
    "when teams",
    "in a product",
    "in production",
    "in a support team",
    "in a startup",
    "in a workflow",
    "today",
    "for example",
    "a company",
    "a builder",
    "a developer",
    "a student",
    "a team",
]

EXAMPLE_MARKERS = [
    "for example",
    "example",
    "such as",
    "like",
    "say",
    "could",
]

LIMITATION_MARKERS = [
    "limitation",
    "tradeoff",
    "trade-off",
    "catch",
    "downside",
    "however",
    "but",
    "the catch",
]

CHALLENGE_MARKERS = [
    "challenge",
    "try this",
    "today",
    "this week",
    "audit",
    "measure",
    "compare",
    "test",
    "evaluate",
]

TECH_TERMS = [
    "model",
    "training",
    "inference",
    "retrieval",
    "fine-tuning",
    "finetuning",
    "adapter",
    "pipeline",
    "evaluation",
    "latency",
    "dataset",
    "workflow",
    "system",
    "prompt",
    "agent",
    "llm",
    "embedding",
    "optimization",
    "adaptation",
]

STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "into", "about", "your",
    "have", "what", "when", "where", "which", "their", "will", "would", "could",
    "should", "there", "then", "than", "them", "they", "you", "our", "were",
    "been", "being", "into", "while", "only", "more", "most", "very", "here",
}


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _has_number(text: str) -> bool:
    return bool(re.search(r"\d", text))


def _contains_cta(text: str) -> bool:
    cta_words = [
        "follow", "profile", "check my profile", "save", "share",
        "comment", "tell me", "what would you", "challenge"
    ]
    t = text.lower()
    return any(w in t for w in cta_words)


def _first_line(text: str) -> str:
    return text.strip().splitlines()[0] if text.strip() else ""


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def _topic_tokens(topic: str) -> list[str]:
    tokens = [t for t in _tokenize(topic) if len(t) > 3 and t not in STOPWORDS]
    return tokens


def _hook_strength(text: str) -> float:
    first = _first_line(text)
    score = 0.0
    if len(first) <= 140:
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
    words = _tokenize(text)
    if not words:
        return 0.0
    avg_len = sum(len(w) for w in words) / len(words)
    score = 100.0
    if avg_len > 6.5:
        score -= min(30, (avg_len - 6.5) * 6)
    if len(words) > settings.max_post_length:
        score -= min(20, (len(words) - settings.max_post_length) * 0.5)
    sentence_count = max(1, len(re.split(r"[.!?]+", text)) - 1)
    if sentence_count < 3:
        score -= 10
    if sentence_count > 8:
        score -= 5
    return _clamp(score)


def _real_world_context_score(text: str) -> float:
    t = text.lower()
    hits = sum(1 for marker in REAL_WORLD_MARKERS if marker in t)
    if hits == 0:
        return 20.0 if text and text[0].islower() is False else 10.0
    return _clamp(35 + hits * 15)


def _example_score(text: str) -> float:
    t = text.lower()
    hits = sum(1 for marker in EXAMPLE_MARKERS if marker in t)
    return _clamp(20 + hits * 16)


def _limitation_score(text: str) -> float:
    t = text.lower()
    hits = sum(1 for marker in LIMITATION_MARKERS if marker in t)
    return _clamp(15 + hits * 18)


def _challenge_score(text: str) -> float:
    t = text.lower()
    hits = sum(1 for marker in CHALLENGE_MARKERS if marker in t)
    return _clamp(20 + hits * 16)


def _simple_language_score(text: str) -> float:
    words = _tokenize(text)
    if not words:
        return 0.0
    avg_len = sum(len(w) for w in words) / len(words)
    long_words = sum(1 for w in words if len(w) > 12)
    score = 100.0
    score -= max(0.0, (avg_len - 5.5) * 12)
    score -= min(20.0, long_words * 2.5)
    if len(words) < 60:
        score -= 8
    return _clamp(score)


def _technical_accuracy_score(text: str, brief: PostBrief) -> float:
    t = text.lower()
    topic_tokens = _topic_tokens(brief.topic)
    topic_hits = sum(1 for tok in topic_tokens if tok in t)
    tech_hits = sum(1 for term in TECH_TERMS if term in t)
    audience_bonus = 15 if brief.audience in t else 0
    score = 20 + topic_hits * 12 + tech_hits * 4 + audience_bonus
    return _clamp(score)


def _utility_score(text: str, brief: PostBrief) -> float:
    t = text.lower()
    score = 0.0
    if any(word in t for word in ["workflow", "system", "process", "steps", "checklist", "framework"]):
        score += 25
    if any(word in t for word in ["practical", "implement", "build", "ship", "useful", "apply"]):
        score += 20
    if brief.audience in t:
        score += 10
    if _has_number(text):
        score += 10
    if len(text.split()) >= 110:
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


def _practical_usefulness_score(real_world: float, example: float, limitation: float, challenge: float, utility: float) -> float:
    return _clamp(0.25 * real_world + 0.20 * example + 0.20 * challenge + 0.15 * limitation + 0.20 * utility)


def _educational_value_score(
    real_world: float,
    example: float,
    limitation: float,
    challenge: float,
    practical: float,
    clarity: float,
    simple_language: float,
    technical_accuracy: float,
) -> float:
    score = (
        0.18 * real_world
        + 0.16 * example
        + 0.16 * limitation
        + 0.12 * challenge
        + 0.12 * practical
        + 0.10 * clarity
        + 0.08 * simple_language
        + 0.08 * technical_accuracy
    )
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
        inputs = processor(text=[text[:128]], images=image, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            img = outputs.image_embeds
            txt = outputs.text_embeds
            img = img / img.norm(dim=-1, keepdim=True)
            txt = txt / txt.norm(dim=-1, keepdim=True)
            sim = (img @ txt.T).squeeze().item()
            return float(_clamp(((sim + 1.0) / 2.0) * 100.0))
    except Exception:
        return 0.0


def evaluate_image_quality(image_path: str) -> Dict[str, float]:
    result = {
        "image_quality_score": 0.0,
        "brightness": 0.0,
        "contrast": 0.0,
        "texture": 0.0,
        "is_black": 0.0,
        "is_blank": 0.0,
        "reason": "",
        "passed": 0.0,
    }

    try:
        img = Image.open(image_path).convert("RGB")
        arr = np.asarray(img).astype(np.float32)
        if arr.size == 0:
            result["reason"] = "empty image"
            return result

        brightness = float(arr.mean() / 255.0)
        contrast = float(arr.std() / 255.0)

        texture = 0.0
        if arr.shape[0] > 1:
            texture += float(np.var(np.diff(arr, axis=0)))
        if arr.shape[1] > 1:
            texture += float(np.var(np.diff(arr, axis=1)))
        texture = texture / (255.0 ** 2)

        is_black = brightness < 0.08 and arr.std() < 10
        is_blank = arr.std() < 6
        score = 100.0
        if is_black:
            score -= 70
        if is_blank:
            score -= 55
        score += min(15.0, contrast * 120.0)
        score += min(10.0, texture * 120.0)
        if brightness < 0.15:
            score -= 15
        if brightness > 0.95 and contrast < 0.08:
            score -= 15

        score = _clamp(score)
        reason = ""
        if is_black:
            reason = "black image"
        elif is_blank:
            reason = "blank image"
        elif score < settings.image_quality_min_score:
            reason = "low image quality"

        result.update({
            "image_quality_score": score,
            "brightness": brightness,
            "contrast": contrast,
            "texture": texture,
            "is_black": 1.0 if is_black else 0.0,
            "is_blank": 1.0 if is_blank else 0.0,
            "reason": reason,
            "passed": 1.0 if (score >= settings.image_quality_min_score and not is_black and not is_blank) else 0.0,
        })
    except Exception as exc:
        result["reason"] = f"image load failed: {exc}"
        result["passed"] = 0.0

    return result


def _image_alignment_score(text: str, image_path: str, image_quality_score: float) -> float:
    clip_pack = _load_clip()
    if clip_pack is None:
        return _clamp(image_quality_score * 0.75)

    return clip_similarity(text, image_path)


def score_text(text: str, brief: PostBrief, history: Dict) -> Dict[str, float]:
    hook = _hook_strength(text)
    clarity = _clarity_score(text)
    real_world = _real_world_context_score(text)
    example = _example_score(text)
    limitation = _limitation_score(text)
    challenge = _challenge_score(text)
    simple_language = _simple_language_score(text)
    technical_accuracy = _technical_accuracy_score(text, brief)
    utility = _utility_score(text, brief)
    novelty = _novelty_score(text, history)
    audience = _audience_score(text, brief)
    cta = 100.0 if _contains_cta(text) else 30.0

    practical_usefulness = _practical_usefulness_score(real_world, example, limitation, challenge, utility)
    educational_value = _educational_value_score(
        real_world,
        example,
        limitation,
        challenge,
        practical_usefulness,
        clarity,
        simple_language,
        technical_accuracy,
    )

    text_quality = (
        0.22 * hook
        + 0.18 * clarity
        + 0.20 * utility
        + 0.14 * novelty
        + 0.12 * audience
        + 0.14 * cta
    )

    profile_visit_probability = _clamp(
        0.22 * novelty
        + 0.20 * hook
        + 0.18 * audience
        + 0.18 * utility
        + 0.12 * cta
        + 0.10 * (100.0 if brief.belief else 0.0)
    )

    follow_probability = _clamp(
        0.45 * profile_visit_probability
        + 0.25 * utility
        + 0.20 * novelty
        + 0.10 * (100.0 if _contains_cta(text) else 0.0)
    )

    save_probability = _clamp(0.40 * utility + 0.30 * clarity + 0.30 * novelty)
    share_probability = _clamp(0.40 * hook + 0.35 * novelty + 0.25 * clarity)
    comment_probability = _clamp(0.60 * hook + 0.40 * audience + (5 if "?" in text else 0))

    follower_score = _clamp(
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
        "real_world_context_score": real_world,
        "example_score": example,
        "limitation_score": limitation,
        "challenge_score": challenge,
        "simple_language_score": simple_language,
        "technical_accuracy": technical_accuracy,
        "practical_usefulness": practical_usefulness,
        "educational_value": educational_value,
        "profile_visit_probability": profile_visit_probability,
        "follow_probability": follow_probability,
        "save_probability": save_probability,
        "share_probability": share_probability,
        "comment_probability": comment_probability,
        "follower_score": follower_score,
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

    title_tokens = len(set(_tokenize(title)))
    score += min(15, title_tokens * 1.5)

    if "?" in title:
        score += 5

    return _clamp(score)


def score_candidate(text: str, image_path: str, brief: PostBrief, history: Dict) -> Dict[str, float]:
    text_scores = score_text(text, brief, history)
    image_quality = evaluate_image_quality(image_path) if image_path else {
        "image_quality_score": 0.0,
        "brightness": 0.0,
        "contrast": 0.0,
        "texture": 0.0,
        "is_black": 1.0,
        "is_blank": 1.0,
        "reason": "missing image",
        "passed": 0.0,
    }

    image_alignment_score = _image_alignment_score(
        f"{brief.topic}. {brief.audience}. {brief.post_type}. {brief.belief}",
        image_path,
        image_quality.get("image_quality_score", 0.0),
    ) if image_path else 0.0

    final = (
        settings.score_weights["educational_value"] * text_scores["educational_value"]
        + settings.score_weights["image_quality"] * image_quality["image_quality_score"]
        + settings.score_weights["image_alignment"] * image_alignment_score
        + settings.score_weights["practical_usefulness"] * text_scores["practical_usefulness"]
        + settings.score_weights["clarity"] * text_scores["clarity"]
        + settings.score_weights["technical_accuracy"] * text_scores["technical_accuracy"]
        + settings.score_weights["profile_visit_probability"] * text_scores["profile_visit_probability"]
        + settings.score_weights["follow_probability"] * text_scores["follow_probability"]
        + settings.score_weights["hook_strength"] * text_scores["hook_strength"]
        + settings.score_weights["novelty"] * text_scores["novelty"]
        + settings.score_weights["cta_strength"] * text_scores["cta_strength"]
        + settings.score_weights["audience_match"] * text_scores["audience_match"]
    )

    repetition = 0.0
    recent = recent_texts(history, limit=settings.recent_post_limit)
    if recent:
        repetition = max(SequenceMatcher(None, normalize_text(text), normalize_text(prev)).ratio() for prev in recent[-25:]) * 100.0

    publish_ready = (
        final >= settings.publish_threshold
        and text_scores["educational_value"] >= settings.educational_min_score
        and text_scores["real_world_context_score"] >= settings.real_world_context_min_score
        and text_scores["example_score"] >= settings.example_min_score
        and text_scores["limitation_score"] >= settings.limitation_min_score
        and text_scores["challenge_score"] >= settings.challenge_min_score
        and image_quality["image_quality_score"] >= settings.image_quality_min_score
        and image_alignment_score >= settings.image_alignment_min_score
        and text_scores["follow_probability"] >= settings.min_follow_probability
        and text_scores["profile_visit_probability"] >= settings.min_profile_visit_probability
        and repetition <= settings.max_repetition_similarity * 100.0
        and image_quality.get("passed", 0.0) >= 1.0
    )

    return {
        **text_scores,
        **image_quality,
        "image_alignment_score": image_alignment_score,
        "clip": image_alignment_score,
        "final_score": _clamp(final),
        "repetition_similarity": repetition,
        "publish_ready": 1.0 if publish_ready else 0.0,
    }


def diagnose_text_failure(metrics: Dict[str, float]) -> str:
    feedback = []

    if metrics.get("real_world_context_score", 0.0) < settings.real_world_context_min_score:
        feedback.append("Start with a real-world situation and tie the topic to a real workflow.")
    if metrics.get("example_score", 0.0) < settings.example_min_score:
        feedback.append("Add one practical example that shows the idea in action.")
    if metrics.get("limitation_score", 0.0) < settings.limitation_min_score:
        feedback.append("Mention one limitation or tradeoff clearly.")
    if metrics.get("challenge_score", 0.0) < settings.challenge_min_score:
        feedback.append("End with one actionable challenge the reader can try today.")
    if metrics.get("simple_language_score", 0.0) < 70:
        feedback.append("Use simpler English and shorter sentences.")
    if metrics.get("clarity", 0.0) < 70:
        feedback.append("Make the explanation cleaner and easier to follow.")
    if metrics.get("technical_accuracy", 0.0) < 60:
        feedback.append("Make the explanation more topic-specific and less generic.")
    if metrics.get("educational_value", 0.0) < settings.educational_min_score:
        feedback.append("Increase the teaching value: explain what it is, why it matters, and what problem it solves.")

    return " ".join(feedback) if feedback else "Make the post clearer, more practical, and more educational."


def diagnose_image_failure(image_metrics: Dict[str, float]) -> str:
    feedback = []
    if image_metrics.get("is_black", 0.0) >= 1.0:
        feedback.append("The image is black. Make it brighter and show a visible subject.")
    if image_metrics.get("is_blank", 0.0) >= 1.0:
        feedback.append("The image is too blank. Add a clear subject and stronger composition.")
    if image_metrics.get("image_quality_score", 0.0) < settings.image_quality_min_score:
        feedback.append("Improve image quality, contrast, detail, and clarity.")
    return " ".join(feedback) if feedback else "Make the image more relevant, cleaner, and more polished."


def diagnose_candidate_failure(metrics: Dict[str, float]) -> Dict[str, str]:
    text_reasons = []
    image_reasons = []

    if metrics.get("educational_value", 0.0) < settings.educational_min_score:
        text_reasons.append("raise educational value")
    if metrics.get("real_world_context_score", 0.0) < settings.real_world_context_min_score:
        text_reasons.append("add real-world context")
    if metrics.get("example_score", 0.0) < settings.example_min_score:
        text_reasons.append("add a practical example")
    if metrics.get("limitation_score", 0.0) < settings.limitation_min_score:
        text_reasons.append("add a limitation or tradeoff")
    if metrics.get("challenge_score", 0.0) < settings.challenge_min_score:
        text_reasons.append("add an actionable challenge")
    if metrics.get("simple_language_score", 0.0) < 70:
        text_reasons.append("simplify the language")
    if metrics.get("technical_accuracy", 0.0) < 60:
        text_reasons.append("make the explanation more topic-specific")
    if metrics.get("clarity", 0.0) < 70:
        text_reasons.append("improve clarity")
    if metrics.get("hook_strength", 0.0) < 60:
        text_reasons.append("make the hook stronger")
    if metrics.get("follow_probability", 0.0) < settings.min_follow_probability:
        text_reasons.append("improve the follow reason")
    if metrics.get("profile_visit_probability", 0.0) < settings.min_profile_visit_probability:
        text_reasons.append("make the post interesting enough to visit the profile")

    if metrics.get("is_black", 0.0) >= 1.0:
        image_reasons.append("fix the black image")
    if metrics.get("is_blank", 0.0) >= 1.0:
        image_reasons.append("add a clear subject to the image")
    if metrics.get("image_quality_score", 0.0) < settings.image_quality_min_score:
        image_reasons.append("improve image quality and contrast")
    if metrics.get("image_alignment_score", 0.0) < settings.image_alignment_min_score:
        image_reasons.append("make the image match the topic better")

    if image_reasons and not text_reasons:
        return {"kind": "image", "feedback": "; ".join(image_reasons)}
    if text_reasons and not image_reasons:
        return {"kind": "text", "feedback": "; ".join(text_reasons)}
    if text_reasons and image_reasons:
        return {"kind": "both", "feedback": f"Text: {'; '.join(text_reasons)}. Image: {'; '.join(image_reasons)}."}

    return {"kind": "final", "feedback": "Improve the overall quality and clarity."}