from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# Trend
# ============================================================

@dataclass
class TrendItem:
    title: str
    summary: str
    url: str
    source: str = ""
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Knowledge Pack
# ============================================================

@dataclass
class KnowledgePack:
    what_happened: str = ""
    why_it_matters: str = ""
    problem_solved: str = ""
    example: str = ""
    limitation: str = ""
    takeaway: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Post Brief
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

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)

        if self.knowledge:
            data["knowledge"] = self.knowledge.to_dict()

        return data


# ============================================================
# Draft Variant
# ============================================================

@dataclass
class DraftVariant:
    text: str

    prompt: str = ""
    score: float = 0.0

    feedback: str = ""

    metrics: Dict[str, Any] = field(default_factory=dict)

    clip_score: float = 0.0
    follower_score: float = 0.0

    profile_visit_probability: float = 0.0
    follow_probability: float = 0.0

    image_path: str = ""
    image_prompt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Candidate Pair
# ============================================================

@dataclass
class CandidatePair:
    brief: PostBrief
    draft: DraftVariant
    final_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "brief": self.brief.to_dict(),
            "draft": self.draft.to_dict(),
            "final_score": self.final_score,
        }


# ============================================================
# Run Record
# ============================================================

@dataclass
class RunRecord:
    run_id: str
    created_at: str

    trend: Dict[str, Any]
    brief: Dict[str, Any]

    best_candidate: Dict[str, Any]

    publish_result: Dict[str, Any]

    metrics: Dict[str, Any]

    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# Publish Result
# ============================================================

@dataclass
class PublishResult:
    success: bool

    post_id: Optional[str] = None
    url: Optional[str] = None

    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
