from __future__ import annotations

import random
from typing import Dict, List, Optional

from config import settings
from models import PostBrief, TrendItem
from storage import normalize_text


AUDIENCE_GUIDANCE = {
    "students": [
        "make it practical for someone learning AI/ML",
        "show what this means for students right now",
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


POST_TYPE_GUIDANCE = {
    "contrarian insight": "write a sharp contrarian LinkedIn post",
    "myth vs reality": "write a myth-busting LinkedIn post",
    "lesson from failure": "write a practical post about a mistake and lesson learned",
    "tool comparison": "write a comparison LinkedIn post",
    "trend breakdown": "write a trend breakdown LinkedIn post",
    "beginner mistake": "write a beginner mistake LinkedIn post",
    "practical tutorial": "write a practical tutorial LinkedIn post",
    "future prediction": "write a future prediction LinkedIn post",
    "case study": "write a concise case study LinkedIn post",
    "one-chart explanation": "write a post explaining a chart or visual insight",
}


BELIEFS = [
    "the people who learn systems will outperform people who only learn tools",
    "AI literacy is becoming a baseline career skill",
    "good workflow design beats random model hopping",
    "the fastest builders win because they simplify repetition",
    "attention is earned by clarity, not noise",
    "small technical advantages compound into big career advantages",
]


HOOK_STYLES = [
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
        "Follow for practical AI/ML breakdowns that actually help builders.",
        "Follow for useful AI and ML systems, not noise.",
    ],
    "profile_visit": [
        "Check my profile for more practical AI/ML breakdowns.",
        "My profile contains detailed AI/ML workflows and systems.",
    ],
    "discussion": [
        "What would you test first?",
        "Which part would you improve?",
    ],
    "resource": [
        "I share the exact systems behind these breakdowns on my profile.",
    ],
    "opinion": [
        "Curious how you would approach this differently.",
    ],
}


IMAGE_STYLES = {
    "editorial cover": "editorial magazine cover, cinematic, high contrast, premium, sharp subject, clean layout",
    "magazine style": "modern magazine cover, realistic, polished, strong focal point",
    "product visualization": "premium product render, realistic lighting",
    "technical diagram": "beautiful technical diagram, modern UX",
    "data visualization": "editorial data visualization scene",
    "before after comparison": "split-screen comparison",
    "realistic future scene": "realistic future workplace",
    "infographic": "high-end infographic style",
}


REAL_WORLD_CONTEXT_RULE = """
REAL-WORLD CONTEXT RULE

Whenever possible:

1. Start with a real-world situation.
2. Explain the AI/ML concept using that situation.
3. Show how the concept solves a problem.
4. Give one practical example.
5. Mention one limitation or tradeoff.
6. End with one actionable challenge.

The challenge should be something the reader can try immediately.
""".strip()


KNOWLEDGE_FIRST_RULE = """
KNOWLEDGE-FIRST RULE

The reader must learn:

- What happened
- Why it matters
- What problem it solves
- How it works
- One practical example
- One limitation
- One actionable takeaway

The post should feel like a mini lesson.
""".strip()


GENERIC_CONTENT_RULE = """
DO NOT WRITE GENERIC CONTENT.

Avoid:

- AI will change everything
- Work smarter
- Leverage AI
- Stay ahead
- Game changer
- Revolutionary
- Future is AI

Every claim should teach something useful.
""".strip()


def _pick(values: List[str], seed: str) -> str:
    rng = random.Random(seed)
    return rng.choice(values)


def select_audience(trend: TrendItem, history: Dict) -> str:
    recent = history.get("audience_history", [])
    options = [a for a in settings.audiences if not recent or recent[-1] != a]
    return _pick(options or settings.audiences, f"{trend.title}|audience")


def select_voice(trend: TrendItem, history: Dict) -> str:
    recent = history.get("voice_history", [])
    options = [v for v in settings.voices if len(recent) < 2 or v not in recent[-2:]]
    return _pick(options or settings.voices, f"{trend.title}|voice")


def select_post_type(trend: TrendItem) -> str:
    return _pick(settings.post_types, f"{trend.title}|post_type")


def select_cta_type(trend: TrendItem, history: Dict) -> str:
    recent = history.get("cta_history", [])
    options = [c for c in settings.cta_types if len(recent) < 2 or c not in recent[-2:]]
    return _pick(options or settings.cta_types, f"{trend.title}|cta")


def select_image_style(trend: TrendItem, history: Dict) -> str:
    recent = history.get("image_styles", [])
    options = [s for s in settings.image_styles if len(recent) < 2 or s not in recent[-2:]]
    return _pick(options or settings.image_styles, f"{trend.title}|image_style")


def build_belief(trend: TrendItem, audience: str) -> str:
    return _pick(BELIEFS, normalize_text(f"{trend.title}|{audience}"))


def build_post_brief(trend: TrendItem, history: Dict) -> PostBrief:
    audience = select_audience(trend, history)
    voice = select_voice(trend, history)

    return PostBrief(
        topic=trend.title,
        audience=audience,
        voice=voice,
        post_type=select_post_type(trend),
        angle=f"{trend.title} for {audience}",
        belief=build_belief(trend, audience),
        cta_type=select_cta_type(trend, history),
        image_style=select_image_style(trend, history),
        source_title=trend.title,
        source_url=trend.url,
        source_summary=trend.summary,
    )


def build_text_prompt(brief: PostBrief, feedback: Optional[str] = None) -> str:

    cta_line = _pick(
        CTA_LIBRARY[brief.cta_type],
        f"{brief.topic}|cta"
    )

    hook_style = _pick(
        HOOK_STYLES,
        f"{brief.topic}|hook"
    )

    feedback_block = ""

    if feedback:
        feedback_block = f"""

FEEDBACK TO FIX:
{feedback}

Only improve the weak sections.
"""

    return f"""
You are a senior AI engineer and educator.

Audience:
{brief.audience}

Voice:
{brief.voice}

Topic:
{brief.topic}

Hook style:
{hook_style}

Source:
{brief.source_title}

Summary:
{brief.source_summary}

{REAL_WORLD_CONTEXT_RULE}

{KNOWLEDGE_FIRST_RULE}

{GENERIC_CONTENT_RULE}

Requirements:

- 140 to 220 words
- Simple English
- Short paragraphs
- Educational
- Practical
- Technical but beginner-friendly
- Explain the concept
- Show a real problem
- Show how AI/ML solves it
- Include one example
- Include one limitation
- Include one challenge
- Include one CTA

Structure:

Hook

Real-world situation

Explanation

Problem solved

Example

Limitation

Challenge

CTA

CTA:
{cta_line}

{feedback_block}
""".strip()


def build_image_prompt(
    brief: PostBrief,
    text: str,
    feedback: Optional[str] = None,
) -> str:

    style = IMAGE_STYLES[brief.image_style]

    return f"""
{style}

Topic:
{brief.topic}

Visual goal:

- Professional
- Editorial
- High contrast
- Premium quality
- LinkedIn optimized
- Realistic
- Strong focal point

Avoid:

- Robots
- Neon brains
- Random AI art
- Watermarks
- Text overlays
- Clutter

Visualize:

{text[:500]}
""".strip()