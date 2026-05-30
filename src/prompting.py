from __future__ import annotations

import random
from dataclasses import asdict
from typing import Dict, List

from config import settings
from models import PostBrief, TrendItem
from storage import normalize_text


AUDIO = {
    "students": [
        "show what this means for students right now",
        "make it practical for someone learning AI/ML",
    ],
    "ai engineers": [
        "show what this means for AI engineers building real systems",
        "focus on implementation, tradeoffs, and workflow",
    ],
    "ml engineers": [
        "focus on model behavior, data, inference, and system design",
        "make it technical but concise",
    ],
    "founders": [
        "translate this into business leverage and opportunity",
        "show product and market implications",
    ],
    "recruiters": [
        "translate this into hiring, skills, and candidate relevance",
        "show what kinds of profiles this will reward",
    ],
    "ctos": [
        "focus on technical strategy, risk, and adoption",
        "show what should be evaluated before adoption",
    ],
    "job seekers": [
        "turn this into career strategy and job-market advantage",
        "show what skill to learn next",
    ],
    "developers": [
        "make it useful for builders shipping quickly",
        "highlight workflow gains and implementation patterns",
    ],
}

ANGLES = [
    "contrarian take",
    "myth-busting perspective",
    "lesson from a failure",
    "tool or workflow comparison",
    "trend breakdown",
    "beginner mistake to avoid",
    "practical tutorial",
    "future prediction",
    "case study",
    "one-chart explanation",
]

BELIEFS = [
    "the people who learn systems will outperform people who only learn tools",
    "AI literacy is becoming a baseline career skill",
    "good workflow design beats random model hopping",
    "the fastest builders win because they simplify repetition",
    "attention is earned by clarity, not by noise",
    "small technical advantages compound into big career advantages",
]

HOOК_STYLES = [
    "surprise",
    "curiosity gap",
    "contrarian",
    "prediction",
    "strong opinion",
    "unexpected statistic",
    "future framing",
]

CTA_LIBRARY = {
    "follow": [
        "Follow for practical AI/ML systems, not noise.",
        "Follow if you want useful AI/ML breakdowns that save time.",
    ],
    "profile_visit": [
        "My profile has more breakdowns like this.",
        "Check my profile for the full AI/ML workflow.",
    ],
    "discussion": [
        "What would you change in this workflow?",
        "Which part of this would you improve first?",
    ],
    "resource": [
        "I can keep posting the exact workflow pieces I use.",
        "I share the process behind these breakdowns on my profile.",
    ],
    "opinion": [
        "Tell me if you disagree with this direction.",
        "Curious how you would approach this differently.",
    ],
}

IMAGE_STYLES = {
    "editorial cover": "editorial magazine cover, cinematic, high contrast, premium, sharp subject, clean layout, no text, no watermark",
    "magazine style": "modern magazine cover, realistic, polished, strong focal point, clean composition, no text, no watermark",
    "product visualization": "premium product render, realistic lighting, clean studio background, minimal, no text, no watermark",
    "technical diagram": "beautiful technical diagram, modern UX, clear arrows, clean labels replaced by visual cues, high contrast, no text, no watermark",
    "data visualization": "editorial data visualization scene, elegant charts, dark professional palette, crisp layout, no text, no watermark",
    "before after comparison": "split-screen before and after comparison, realistic, dramatic, clean layout, no text, no watermark",
    "realistic future scene": "realistic future workplace, professionals using AI systems, cinematic photography, natural lighting, no text, no watermark",
    "infographic": "high-end infographic style, minimal, balanced spacing, visual hierarchy, no text, no watermark",
}


def _pick(values: List[str], seed: str) -> str:
    rng = random.Random(seed)
    return rng.choice(values)


def select_audience(trend: TrendItem, history: Dict) -> str:
    seed = f"{trend.title}|audience"
    return _pick(settings.audiences, seed)


def select_voice(trend: TrendItem, history: Dict) -> str:
    recent = history.get("voice_history", [])
    options = [v for v in settings.voices if not recent or recent[-1] != v]
    if not options:
        options = settings.voices
    return _pick(options, f"{trend.title}|voice")


def select_post_type(trend: TrendItem, history: Dict) -> str:
    return _pick(settings.post_types, f"{trend.title}|post_type")


def select_cta_type(trend: TrendItem, history: Dict) -> str:
    recent = history.get("cta_history", [])
    options = [c for c in settings.cta_types if len(recent) < 2 or c not in recent[-2:]]
    if not options:
        options = settings.cta_types
    return _pick(options, f"{trend.title}|cta")


def select_image_style(trend: TrendItem, history: Dict) -> str:
    recent = history.get("image_styles", [])
    options = [s for s in settings.image_styles if len(recent) < 2 or s not in recent[-2:]]
    if not options:
        options = settings.image_styles
    return _pick(options, f"{trend.title}|image_style")


def build_belief(trend: TrendItem, audience: str) -> str:
    seed = normalize_text(f"{trend.title}|{audience}")
    return _pick(BELIEFS, seed)


def build_post_brief(trend: TrendItem, history: Dict) -> PostBrief:
    audience = select_audience(trend, history)
    voice = select_voice(trend, history)
    post_type = select_post_type(trend, history)
    cta_type = select_cta_type(trend, history)
    image_style = select_image_style(trend, history)
    belief = build_belief(trend, audience)
    angle = f"{post_type} for {audience}"
    return PostBrief(
        topic=trend.title,
        audience=audience,
        voice=voice,
        post_type=post_type,
        angle=angle,
        belief=belief,
        cta_type=cta_type,
        image_style=image_style,
        source_title=trend.title,
        source_url=trend.url,
        source_summary=trend.summary,
    )


def build_text_prompt(brief: PostBrief) -> str:
    cta_line = random.choice(CTA_LIBRARY[brief.cta_type])
    hook_style = _pick(HOOК_STYLES, f"{brief.topic}|hook")
    format_instruction = {
    "contrarian insight":
        "write a contrarian LinkedIn post",

    "myth vs reality":
        "write a myth-busting LinkedIn post",

    "lesson from failure":
        "write a reflective LinkedIn post about lessons learned",

    "tool comparison":
        "write a tool comparison LinkedIn post",

    "trend breakdown":
        "write a trend analysis LinkedIn post",

    "beginner mistake":
        "write a beginner mistake LinkedIn post",

    "practical tutorial":
        "write a practical tutorial LinkedIn post",

    "future prediction":
        "write a future prediction LinkedIn post",

    "case study":
        "write a concise case study LinkedIn post",

    "one-chart explanation":
        "write a post explaining a chart or visualization",
}.get(
    brief.post_type,
    "write a professional LinkedIn post"
)

    return f"""
You are writing for LinkedIn.

Audience: {brief.audience}
Voice: {brief.voice}
Post type: {brief.post_type}
Angle: {brief.angle}
Belief to reinforce: {brief.belief}
Hook style: {hook_style}

Write {format_instruction} about: {brief.topic}

Hard requirements:
- 110 to 180 words.
- Strong first line with a clear attention hook.
- No generic intro like "In today's world".
- One concrete insight that is useful immediately.
- One short example or consequence.
- Short paragraphs with line breaks for LinkedIn readability.
- Keep it human, sharp, and specific.
- Do not repeat the topic title verbatim more than once.
- No hashtags unless they are truly necessary. Max 2.
- End with this CTA style: {cta_line}

The post must feel like a top creator wrote it, not a template.
""".strip()


def build_image_prompt(brief: PostBrief, text: str) -> str:
    base_style = IMAGE_STYLES[brief.image_style]
    return f"""
{base_style}

Scene direction:
- Topic: {brief.topic}
- Audience: {brief.audience}
- Emotional tone: curiosity, authority, clarity
- Visual story: show the real-world implication of the post
- Composition: one dominant subject, strong negative space, premium LinkedIn thumbnail energy
- Quality: ultra-detailed, realistic, editorial, not cartoonish
- Avoid: robots, neon brains, abstract nonsense, text overlays, watermarks, clutter
- Match this post:
{text[:450]}
""".strip()