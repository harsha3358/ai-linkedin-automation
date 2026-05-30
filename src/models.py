from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TrendItem:
    title: str
    source: str
    url: str
    summary: str = ""
    published_at: str = ""
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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
    source_title: str = ""
    source_url: str = ""
    source_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DraftVariant:
    text: str
    prompt: str = ""
    score: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    image_path: str = ""
    image_prompt: str = ""
    clip_score: float = 0.0
    follower_score: float = 0.0
    profile_visit_probability: float = 0.0
    follow_probability: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CandidatePair:
    brief: PostBrief
    draft: DraftVariant
    final_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "brief": self.brief.to_dict(),
            "draft": self.draft.to_dict(),
            "final_score": self.final_score,
        }


@dataclass
class PublishResult:
    published: bool
    status_code: int = 0
    response_text: str = ""
    post_urn: str = ""
    asset_urn: str = ""
    post_url: str = ""
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RunRecord:
    run_id: str
    created_at: str
    trend: Dict[str, Any]
    brief: Dict[str, Any]
    best_candidate: Dict[str, Any]
    publish_result: Dict[str, Any]
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)