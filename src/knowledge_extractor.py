from dataclasses import dataclass
from typing import Dict


@dataclass
class KnowledgePack:
    what_happened: str
    why_it_matters: str
    problem_solved: str
    example: str
    limitation: str
    takeaway: str


def extract_knowledge(trend) -> KnowledgePack:
    """
    Converts a trend/article into structured knowledge.
    """

    title = getattr(trend, "title", "")
    summary = getattr(trend, "summary", "")

    return KnowledgePack(
        what_happened=title,
        why_it_matters=f"This trend could impact how AI/ML systems are built and used.",
        problem_solved=f"The core goal is to solve a real-world bottleneck related to {title}.",
        example=f"A company could test {title} in a small workflow before wider adoption.",
        limitation="Every AI approach introduces tradeoffs such as complexity, cost, latency, or maintenance.",
        takeaway=f"Evaluate whether {title} can improve an existing workflow before replacing current systems."
    )


def to_dict(pack: KnowledgePack) -> Dict:
    return {
        "what_happened": pack.what_happened,
        "why_it_matters": pack.why_it_matters,
        "problem_solved": pack.problem_solved,
        "example": pack.example,
        "limitation": pack.limitation,
        "takeaway": pack.takeaway,
    }