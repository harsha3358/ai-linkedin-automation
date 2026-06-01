from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


def env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


@dataclass(frozen=True)
class Settings:
    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "data")
    output_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "outputs")
    history_file: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "data" / "history.json")
    runs_file: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "data" / "runs.json")

    # Providers
    model_provider: str = field(default_factory=lambda: env("MODEL_PROVIDER", "gemini"))
    image_provider: str = field(default_factory=lambda: env("IMAGE_PROVIDER", "hf"))

    # Models
    text_model: str = field(default_factory=lambda: env("TEXT_MODEL", "gemini-2.5-flash"))
    fallback_text_model: str = field(default_factory=lambda: env("FALLBACK_TEXT_MODEL", "google/flan-t5-base"))

    image_model: str = field(
        default_factory=lambda: env(
            "IMAGE_MODEL",
            "stabilityai/sd-turbo"
        )
    )

    fallback_image_model: str = field(
        default_factory=lambda: env(
            "FALLBACK_IMAGE_MODEL",
            "runwayml/stable-diffusion-v1-5"
        )
    )

    # Multi-agent model knobs
    research_model: str = field(default_factory=lambda: env("RESEARCH_MODEL", "gemini-2.5-flash"))
    writer_model: str = field(default_factory=lambda: env("WRITER_MODEL", "gemini-2.5-flash"))
    critic_model: str = field(default_factory=lambda: env("CRITIC_MODEL", "gemini-2.5-flash"))

    # API keys
    google_api_key: str = field(default_factory=lambda: env("GEMINI_API_KEY"))

    huggingface_token: str = field(
        default_factory=lambda:
        env("HF_TOKEN")
        or env("HF_API_KEY")
        or env("HUGGINGFACE_HUB_TOKEN")
    )

    openai_api_key: str = field(default_factory=lambda: env("OPENAI_API_KEY"))
    openrouter_api_key: str = field(default_factory=lambda: env("OPENROUTER_API_KEY"))
    news_api_key: str = field(default_factory=lambda: env("NEWS_API_KEY"))

    linkedin_access_token: str = field(
        default_factory=lambda: env("LINKEDIN_ACCESS_TOKEN")
    )

    linkedin_client_id: str = field(
        default_factory=lambda: env("LINKEDIN_CLIENT_ID")
    )

    linkedin_client_secret: str = field(
        default_factory=lambda: env("LINKEDIN_CLIENT_SECRET")
    )

    linkedin_person_urn: str = field(
        default_factory=lambda: env("LINKEDIN_PERSON_URN")
    )

    # Generation Settings
    topics_per_run: int = 2

    text_variants_per_topic: int = 2

    image_variants_per_text: int = 1

    max_text_retries: int = 1

    max_image_retries: int = 1

    max_repair_rounds: int = 1

    max_post_length: int = 150

    min_post_length: int = 100

    cta_rotation_window: int = 5

    recent_post_limit: int = 100

    recent_topic_limit: int = 100

    # Quality Thresholds
    clip_threshold: float = 0.35

    publish_threshold: float = 74.0

    educational_min_score: float = 75.0

    image_quality_min_score: float = 70.0

    image_alignment_min_score: float = 65.0

    real_world_context_min_score: float = 70.0

    example_min_score: float = 60.0

    limitation_min_score: float = 60.0

    challenge_min_score: float = 60.0

    min_follow_probability: float = 70.0

    min_profile_visit_probability: float = 68.0

    max_repetition_similarity: float = 0.70

    # Main Scoring Weights
    score_weights: Dict[str, float] = field(default_factory=lambda: {
        "educational_value": 0.26,
        "image_quality": 0.15,
        "image_alignment": 0.10,
        "practical_usefulness": 0.12,
        "clarity": 0.08,
        "technical_accuracy": 0.05,
        "profile_visit_probability": 0.08,
        "follow_probability": 0.08,
        "hook_strength": 0.04,
        "novelty": 0.02,
        "cta_strength": 0.01,
        "audience_match": 0.01,
    })

    # Follower Growth Weights
    follower_score_weights: Dict[str, float] = field(default_factory=lambda: {
        "profile_visit_probability": 0.25,
        "follow_probability": 0.30,
        "save_probability": 0.20,
        "share_probability": 0.15,
        "comment_probability": 0.10,
    })

    audiences: List[str] = field(default_factory=lambda: [
        "students",
        "ai engineers",
        "ml engineers",
        "founders",
        "recruiters",
        "ctos",
        "job seekers",
        "developers",
    ])

    voices: List[str] = field(default_factory=lambda: [
        "research analyst",
        "contrarian builder",
        "ai founder",
        "future predictor",
        "practical engineer",
        "industry insider",
        "ceo",
        "cto",
        "startup founder",
        "principal engineer",
    ])

    post_types: List[str] = field(default_factory=lambda: [
        "contrarian insight",
        "myth vs reality",
        "lesson from failure",
        "tool comparison",
        "trend breakdown",
        "beginner mistake",
        "practical tutorial",
        "future prediction",
        "case study",
        "one-chart explanation",
    ])

    cta_types: List[str] = field(default_factory=lambda: [
        "follow",
        "profile_visit",
        "discussion",
        "resource",
        "opinion",
    ])

    image_styles: List[str] = field(default_factory=lambda: [
        "editorial cover",
        "magazine style",
        "product visualization",
        "technical diagram",
        "data visualization",
        "before after comparison",
        "realistic future scene",
        "infographic",
    ])

    trend_sources: List[str] = field(default_factory=lambda: [
        "hackernews",
        "arxiv",
        "reddit",
        "github",
        "newsapi",
    ])


settings = Settings()

settings.data_dir.mkdir(
    parents=True,
    exist_ok=True,
)

settings.output_dir.mkdir(
    parents=True,
    exist_ok=True,
)
