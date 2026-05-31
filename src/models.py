from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# Trend Models
# ============================================================

@dataclass
class TrendItem:
    title: str
    summary: str
    url: str
    source: str = ""
    score: float = 0.0
    metadata: Dict = field(default_factory=dict)


# ============================================================
# Knowledge Models
# ============================================================

@dataclass
class KnowledgePack:
    what_happened: str
    why_it_matters: str
    problem_solved: str
    example: str
    limitation: str
    takeaway: str


# ============================================================
# Content Planning
# ============================================================

@dataclass
class PostBrief:
    topic: str
    audience: str
    voice: str
    post_type: str
    angle: str
    belief: str
    cta_type: str
    image_style: str

    source_title: str
    source_url: str
    source_summary: str

    knowledge: Optional[KnowledgePack] = None


# ============================================================
# Draft Variant
# ============================================================

@dataclass
class DraftVariant:
    text: str
    audience: str = ""
    voice: str = ""
    score: float = 0.0
    feedback: str = ""


# ============================================================
# Candidate Pair
# ============================================================

@dataclass
class CandidatePair:
    text: str
    image_path: str

    text_metrics: Dict = field(default_factory=dict)
    image_metrics: Dict = field(default_factory=dict)

    total_score: float = 0.0


# ============================================================
# Generic Candidate
# ============================================================

@dataclass
class Candidate:
    text: str
    image_path: str

    text_metrics: Dict = field(default_factory=dict)
    image_metrics: Dict = field(default_factory=dict)

    total_score: float = 0.0


# ============================================================
# Run Record
# ============================================================

@dataclass
class RunRecord:
    timestamp: str = ""

    topic: str = ""
    audience: str = ""

    score: float = 0.0

    text: str = ""
    image_path: str = ""

    metrics: Dict = field(default_factory=dict)

    published: bool = False
    publish_url: str = ""


# ============================================================
# Publish Result
# ============================================================

@dataclass
class PublishResult:
    success: bool
    post_id: Optional[str] = None
    url: Optional[str] = None
    message: str = ""


# ============================================================
# Learning
# ============================================================

@dataclass
class LearningStats:
    best_topics: List = field(default_factory=list)
    best_hooks: List = field(default_factory=list)
    best_audiences: List = field(default_factory=list)
    best_ctas: List = field(default_factory=list)
    best_image_styles: List = field(default_factory=list)


# ============================================================
# Failure Analytics
# ============================================================

@dataclass
class FailureRecord:
    failure_type: str
    failure_reason: str
    critic_feedback: str = ""
    timestamp: str = ""


# ============================================================
# Run Result
# ============================================================

@dataclass
class RunResult:
    ok: bool

    score: float = 0.0

    topic: str = ""
    audience: str = ""

    text: str = ""
    image_path: str = ""

    reason: str = ""

    metrics: Dict = field(default_factory=dict)
