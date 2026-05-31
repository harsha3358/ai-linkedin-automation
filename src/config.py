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

    # =====================================================
    # PROJECT PATHS
    # =====================================================

    project_root: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent
    )

    data_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent / "data"
    )

    output_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent / "outputs"
    )

    history_file: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parent
            / "data"
            / "history.json"
        )
    )

    runs_file: Path = field(
        default_factory=lambda: (
            Path(__file__).resolve().parent
            / "data"
            / "runs.json"
        )
    )

    # =====================================================
    # MODEL PROVIDERS
    # =====================================================

    model_provider: str = field(
        default_factory=lambda: env(
            "MODEL_PROVIDER",
            "gemini"
        )
    )

    image_provider: str = field(
        default_factory=lambda: env(
            "IMAGE_PROVIDER",
            "hf"
        )
    )

    # =====================================================
    # MODELS
    # =====================================================

    text_model: str = field(
        default_factory=lambda: env(
            "TEXT_MODEL",
            "gemini-2.5-flash"
        )
    )

    fallback_text_model: str = field(
        default_factory=lambda: env(
            "FALLBACK_TEXT_MODEL",
            "google/flan-t5-base"
        )
    )

    image_model: str = field(
        default_factory=lambda: env(
            "IMAGE_MODEL",
            "black-forest-labs/FLUX.1-schnell"
        )
    )

    fallback_image_model: str = field(
        default_factory=lambda: env(
            "FALLBACK_IMAGE_MODEL",
            "stabilityai/stable-diffusion-xl-base-1.0"
        )
    )

    # =====================================================
    # MULTI-AGENT MODELS
    # =====================================================

    research_model: str = field(
        default_factory=lambda: env(
            "RESEARCH_MODEL",
            "gemini-2.5-flash"
        )
    )

    writer_model: str = field(
        default_factory=lambda: env(
            "WRITER_MODEL",
            "gemini-2.5-flash"
        )
    )

    critic_model: str = field(
        default_factory=lambda: env(
            "CRITIC_MODEL",
            "gemini-2.5-flash"
        )
    )

    # =====================================================
    # API KEYS
    # =====================================================

    google_api_key: str = field(
        default_factory=lambda: env(
            "GEMINI_API_KEY"
        )
    )

    huggingface_token: str = field(
        default_factory=lambda: (
            env("HF_TOKEN")
            or env("HF_API_KEY")
        )
    )

    openai_api_key: str = field(
        default_factory=lambda: env(
            "OPENAI_API_KEY"
        )
    )

    openrouter_api_key: str = field(
        default_factory=lambda: env(
            "OPENROUTER_API_KEY"
        )
    )

    linkedin_access_token: str = field(
        default_factory=lambda: env(
            "LINKEDIN_ACCESS_TOKEN"
        )
    )

    linkedin_client_id: str = field(
        default_factory=lambda: env(
            "LINKEDIN_CLIENT_ID"
        )
    )

    linkedin_client_secret: str = field(
        default_factory=lambda: env(
            "LINKEDIN_CLIENT_SECRET"
        )
    )

    linkedin_person_urn: str = field(
        default_factory=lambda: env(
            "LINKEDIN_PERSON_URN"
        )
    )

    # =====================================================
    # GENERATION SETTINGS
    # =====================================================

    topics_per_run: int = 5

    text_variants_per_topic: int = 8

    # Reduced from 2 → 1 for GitHub Actions stability
    image_variants_per_text: int = 1

    max_post_length: int = 220

    min_post_length: int = 90

    cta_rotation_window: int = 5

    recent_post_limit: int = 100

    recent_topic_limit: int = 100

    # =====================================================
    # QUALITY THRESHOLDS
    # =====================================================

    clip_threshold: float = 0.35

    publish_threshold: float = 68.0

    min_follow_probability: float = 75.0

    min_profile_visit_probability: float = 70.0

    max_repetition_similarity: float = 0.70

    # =====================================================
    # SCORING WEIGHTS
    # =====================================================

    score_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "text_quality": 0.28,
            "hook_strength": 0.16,
            "audience_match": 0.10,
            "novelty": 0.10,
            "clarity": 0.10,
            "utility": 0.08,
            "cta_strength": 0.08,
            "clip": 0.10,
        }
    )

    follower_score_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "profile_visit_probability": 0.25,
            "follow_probability": 0.30,
            "save_probability": 0.20,
            "share_probability": 0.15,
            "comment_probability": 0.10,
        }
    )

    # =====================================================
    # AUDIENCES
    # =====================================================

    audiences: List[str] = field(
        default_factory=lambda: [
            "students",
            "ai engineers",
            "ml engineers",
            "founders",
            "recruiters",
            "ctos",
            "job seekers",
            "developers",
        ]
    )

    # =====================================================
    # CONTENT VOICES
    # =====================================================

    voices: List[str] = field(
        default_factory=lambda: [
            "research analyst",
            "contrarian builder",
            "ai founder",
            "future predictor",
            "practical engineer",
            "industry insider","ceo",
            "cto",
            "venture capitalist",
            "startup founder",
            "principal engineer",
        ]
    )

    # =====================================================
    # POST TYPES
    # =====================================================

    post_types: List[str] = field(
        default_factory=lambda: [
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
        ]
    )

    # =====================================================
    # CTA TYPES
    # =====================================================

    cta_types: List[str] = field(
        default_factory=lambda: [
            "follow",
            "profile_visit",
            "discussion",
            "resource",
            "opinion",
        ]
    )

    # =====================================================
    # IMAGE STYLES
    # =====================================================

    image_styles: List[str] = field(
        default_factory=lambda: [
            "editorial cover",
            "magazine style",
            "product visualization",
            "technical diagram",
            "data visualization",
            "before after comparison",
            "realistic future scene",
            "infographic",
        ]
    )

    # =====================================================
    # TREND SOURCES
    # =====================================================

    trend_sources: List[str] = field(
        default_factory=lambda: [
            "hackernews",
            "reddit",
            "github",
            "arxiv",
        ]
    )


settings = Settings()

settings.data_dir.mkdir(
    parents=True,
    exist_ok=True
)

settings.output_dir.mkdir(
    parents=True,
    exist_ok=True
)
