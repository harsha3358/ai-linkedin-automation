from __future__ import annotations

from knowledge_extractor import extract_knowledge
from content_scheduler import choose_next_post_type
from weekly_learning import get_recommendations
from failure_analytics import (
    create_failure_record,
    store_failure,
)

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import settings
from image_generator import generate_image
from linkedin_client import post_to_linkedin
from models import CandidatePair, DraftVariant, RunRecord, TrendItem
from prompting import build_post_brief, build_image_prompt
from scoring import (
    diagnose_candidate_failure,
    diagnose_image_failure,
    diagnose_text_failure,
    score_candidate,
    score_text,
)
from storage import append_history, load_history, load_runs, save_history, save_runs
from text_generator import generate_post_text
from trend_sources import fetch_trends


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text_passes_gate(metrics: Dict[str, float]) -> bool:
    return (
        metrics.get("educational_value", 0.0) >= settings.educational_min_score
        and metrics.get("real_world_context_score", 0.0) >= settings.real_world_context_min_score
        and metrics.get("example_score", 0.0) >= settings.example_min_score
        and metrics.get("limitation_score", 0.0) >= settings.limitation_min_score
        and metrics.get("challenge_score", 0.0) >= settings.challenge_min_score
        and metrics.get("simple_language_score", 0.0) >= 65.0
        and metrics.get("clarity", 0.0) >= 70.0
    )


def _image_passes_gate(metrics: Dict[str, float]) -> bool:
    return (
        metrics.get("passed", 0.0) >= 1.0
        and metrics.get("image_quality_score", 0.0) >= settings.image_quality_min_score
        and metrics.get("image_alignment_score", 0.0) >= settings.image_alignment_min_score
    )


def _generate_text_variant(
    brief,
    history: Dict,
    seed: int,
) -> Tuple[DraftVariant, Dict[str, float]]:
    best_draft: Optional[DraftVariant] = None
    best_metrics: Dict[str, float] = {}
    feedback: Optional[str] = None

    for attempt in range(settings.max_text_retries):
        draft = generate_post_text(brief, seed=seed + attempt, feedback=feedback)
        metrics = score_text(draft.text, brief, history)

        if best_draft is None or metrics.get("educational_value", 0.0) > best_metrics.get("educational_value", 0.0):
            best_draft = draft
            best_metrics = metrics

        if _text_passes_gate(metrics):
            return draft, metrics

        feedback = diagnose_text_failure(metrics)

    return best_draft or DraftVariant(text="", prompt=""), best_metrics


def _generate_image_variant(
    brief,
    text: str,
    out_dir: Path,
    seed_tag: str,
) -> Tuple[Optional[str], Dict[str, float]]:
    best_path: Optional[str] = None
    best_metrics: Dict[str, float] = {}
    feedback: Optional[str] = None

    for attempt in range(settings.max_image_retries):
        image_path = generate_image(
            brief=brief,
            text=text,
            out_dir=out_dir,
            seed_tag=f"{seed_tag}_{attempt}",
            feedback=feedback,
        )
        if not image_path:
            feedback = "The image generation failed. Make the image brighter, more detailed, and more relevant."
            continue

        from scoring import evaluate_image_quality  # local import to avoid circular / heavy import cost

        image_metrics = evaluate_image_quality(image_path)
        if not best_metrics or image_metrics.get("image_quality_score", 0.0) > best_metrics.get("image_quality_score", 0.0):
            best_path = image_path
            best_metrics = image_metrics

        if _image_passes_gate(image_metrics):
            return image_path, image_metrics

        feedback = diagnose_image_failure(image_metrics)

    return best_path, best_metrics


def _repair_candidate_once(
    brief,
    history: Dict,
    out_dir: Path,
    seed: int,
    current_text: str,
    current_metrics: Dict[str, float],
    current_image_path: Optional[str],
) -> Tuple[str, Optional[str], Dict[str, float]]:
    diagnosis = diagnose_candidate_failure(current_metrics)
    kind = diagnosis.get("kind", "final")
    feedback = diagnosis.get("feedback", "")

    if kind == "text" or kind == "both":
        repaired_draft, repaired_text_metrics = _generate_text_variant(
            brief=brief,
            history=history,
            seed=seed + 100,
        )
        # Re-run with feedback if we have a clear diagnosis.
        if feedback:
            repaired_draft = generate_post_text(brief, seed=seed + 101, feedback=feedback)
            repaired_text_metrics = score_text(repaired_draft.text, brief, history)

        current_text = repaired_draft.text or current_text
        current_metrics = repaired_text_metrics or current_metrics
        current_image_path = None

    if kind == "image" or kind == "both":
        new_image_path, image_metrics = _generate_image_variant(
            brief=brief,
            text=current_text,
            out_dir=out_dir,
            seed_tag=f"{seed}_repair",
        )
        if new_image_path:
            current_image_path = new_image_path
            current_metrics = {**current_metrics, **image_metrics}

    return current_text, current_image_path, current_metrics


def build_candidate(trend: TrendItem, history: Dict, out_dir: Path, seed: int) -> Optional[CandidatePair]:
    brief = build_post_brief(trend, history)
    draft, text_metrics = _generate_text_variant(brief, history, seed=seed)

    if not draft.text:
        return None

    if not _text_passes_gate(text_metrics):
        repaired_text, repaired_image, repaired_metrics = _repair_candidate_once(
            brief=brief,
            history=history,
            out_dir=out_dir,
            seed=seed,
            current_text=draft.text,
            current_metrics=text_metrics,
            current_image_path=None,
        )
        draft.text = repaired_text
        text_metrics = repaired_metrics

    image_path, image_metrics = _generate_image_variant(
        brief=brief,
        text=draft.text,
        out_dir=out_dir,
        seed_tag=str(seed),
    )

    if image_path is None:
        return None

    if not _image_passes_gate(image_metrics):
        repaired_text, repaired_image, repaired_metrics = _repair_candidate_once(
            brief=brief,
            history=history,
            out_dir=out_dir,
            seed=seed,
            current_text=draft.text,
            current_metrics={**text_metrics, **image_metrics},
            current_image_path=image_path,
        )
        draft.text = repaired_text
        if repaired_image:
            image_path = repaired_image

    if image_path is None:
        return None

    metrics = score_candidate(draft.text, image_path, brief, history)

    # One final repair round if the full score is still weak.
    if not metrics.get("publish_ready", 0.0) and settings.max_repair_rounds > 0:
        for repair_round in range(settings.max_repair_rounds):
            diagnosis = diagnose_candidate_failure(metrics)
            kind = diagnosis.get("kind", "final")
            if kind == "final":
                break

            if kind in {"text", "both"}:
                draft = generate_post_text(brief, seed=seed + 200 + repair_round, feedback=diagnosis.get("feedback"))
                if not draft.text:
                    break
                image_path, _ = _generate_image_variant(
                    brief=brief,
                    text=draft.text,
                    out_dir=out_dir,
                    seed_tag=f"{seed}_final_repair_{repair_round}",
                )
                if not image_path:
                    break
                metrics = score_candidate(draft.text, image_path, brief, history)
                if metrics.get("publish_ready", 0.0):
                    break
            elif kind == "image":
                image_path, _ = _generate_image_variant(
                    brief=brief,
                    text=draft.text,
                    out_dir=out_dir,
                    seed_tag=f"{seed}_image_repair_{repair_round}",
                )
                if not image_path:
                    break
                metrics = score_candidate(draft.text, image_path, brief, history)
                if metrics.get("publish_ready", 0.0):
                    break

    draft.metrics = metrics
    draft.score = metrics.get("final_score", 0.0)
    draft.clip_score = metrics.get("image_alignment_score", 0.0)
    draft.follower_score = metrics.get("follower_score", 0.0)
    draft.profile_visit_probability = metrics.get("profile_visit_probability", 0.0)
    draft.follow_probability = metrics.get("follow_probability", 0.0)
    draft.image_path = image_path
    draft.image_prompt = build_image_prompt(brief, draft.text)
    return CandidatePair(brief=brief, draft=draft, final_score=metrics.get("final_score", 0.0))


def generate_candidates(trend: TrendItem, history: Dict, out_dir: Path) -> List[CandidatePair]:
    candidates: List[CandidatePair] = []
    for seed in range(settings.text_variants_per_topic):
        candidate = build_candidate(trend, history, out_dir, seed=seed)
        if candidate:
            candidates.append(candidate)
    return sorted(candidates, key=lambda c: (c.draft.metrics.get("publish_ready", 0.0), c.final_score), reverse=True)


def select_best(trends: List[TrendItem], history: Dict, out_dir: Path) -> Optional[CandidatePair]:
    all_candidates: List[CandidatePair] = []
    for trend in trends[: settings.topics_per_run]:
        all_candidates.extend(generate_candidates(trend, history, out_dir=out_dir))

    if not all_candidates:
        return None

    publish_ready_candidates = [c for c in all_candidates if c.draft.metrics.get("publish_ready", 0.0) >= 1.0]
    if publish_ready_candidates:
        return sorted(publish_ready_candidates, key=lambda c: c.final_score, reverse=True)[0]

    return sorted(all_candidates, key=lambda c: c.final_score, reverse=True)[0]


def update_history(history: Dict, best: CandidatePair, publish_result: Dict) -> Dict:
    record = {
        "created_at": _utc_now(),
        "topic": best.brief.topic,
        "audience": best.brief.audience,
        "voice": best.brief.voice,
        "post_type": best.brief.post_type,
        "image_style": best.brief.image_style,
        "cta_type": best.brief.cta_type,
        "text": best.draft.text,
        "image_path": best.draft.image_path,
        "scores": best.draft.metrics,
        "final_score": best.final_score,
        "publish_result": publish_result,
    }

    history = append_history(history, record, best.draft.text)
    history.setdefault("topics", []).append(best.brief.topic)
    history.setdefault("cta_history", []).append(best.brief.cta_type)
    history.setdefault("voice_history", []).append(best.brief.voice)
    history.setdefault("image_styles", []).append(best.brief.image_style)

    history["topics"] = history["topics"][-settings.recent_topic_limit :]
    history["cta_history"] = history["cta_history"][-settings.cta_rotation_window :]
    history["voice_history"] = history["voice_history"][-settings.cta_rotation_window :]
    history["image_styles"] = history["image_styles"][-settings.cta_rotation_window :]

    return history


def run(dry_run: bool = False) -> Dict:
    history = load_history()
    trends = fetch_trends(limit=settings.topics_per_run)
    out_dir = settings.output_dir / datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    best = select_best(trends, history, out_dir)
    if best is None:
        return {"ok": False, "reason": "No valid candidate produced"}

    publish_result = {"published": False, "dry_run": dry_run}
    published = False

    if not dry_run and best.draft.metrics.get("publish_ready", 0.0) >= 1.0:
        result = post_to_linkedin(best.draft.text, image_path=best.draft.image_path)
        publish_result = result.to_dict()
        published = bool(publish_result.get("published", False))
    elif not dry_run:
        publish_result["reason"] = "Best candidate did not pass the publish gate"

    history = update_history(history, best, publish_result)
    save_history(history)

    run_record = RunRecord(
        run_id=out_dir.name,
        created_at=_utc_now(),
        trend=best.brief.to_dict(),
        brief=best.brief.to_dict(),
        best_candidate=best.to_dict(),
        publish_result=publish_result,
        metrics=best.draft.metrics,
        notes=[],
    )

    runs = load_runs()
    runs.append(run_record.to_dict())
    save_runs(runs)

    if dry_run:
        return {
            "ok": True,
            "run_id": run_record.run_id,
            "topic": best.brief.topic,
            "final_score": best.final_score,
            "publish_ready": bool(best.draft.metrics.get("publish_ready", 0.0) >= 1.0),
            "published": False,
            "text": best.draft.text,
            "image_path": best.draft.image_path,
            "scores": best.draft.metrics,
            "publish_result": publish_result,
        }

    if not published:
        return {
            "ok": False,
            "run_id": run_record.run_id,
            "topic": best.brief.topic,
            "final_score": best.final_score,
            "published": False,
            "text": best.draft.text,
            "image_path": best.draft.image_path,
            "scores": best.draft.metrics,
            "publish_result": publish_result,
            "reason": publish_result.get("error") or publish_result.get("reason") or "Publish gate failed",
        }

    return {
        "ok": True,
        "run_id": run_record.run_id,
        "topic": best.brief.topic,
        "final_score": best.final_score,
        "published": True,
        "text": best.draft.text,
        "image_path": best.draft.image_path,
        "scores": best.draft.metrics,
        "publish_result": publish_result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AI LinkedIn automation v3")
    parser.add_argument("--dry-run", action="store_true", help="Generate everything but do not post to LinkedIn")
    args = parser.parse_args()

    result = run(dry_run=args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
