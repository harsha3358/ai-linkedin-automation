from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from image_generator import generate_image
from linkedin_client import post_to_linkedin
from models import CandidatePair, RunRecord
from prompting import build_post_brief, build_image_prompt
from scoring import score_candidate
from storage import (
    append_history,
    load_history,
    save_history,
    save_runs,
    load_runs,
)
from text_generator import generate_post_text
from trend_sources import fetch_trends


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def generate_candidates(
    trend,
    history,
    out_dir
):

    brief = build_post_brief(
        trend,
        history
    )

    candidates = []

    for idx in range(
        settings.text_variants_per_topic
    ):

        draft = generate_post_text(
            brief,
            seed=idx
        )

        if len(draft.text.split()) < 50:
            continue

        image_path = generate_image(
            brief,
            draft.text,
            out_dir,
            str(idx)
        )

        if not image_path:
            continue

        metrics = score_candidate(
            draft.text,
            image_path,
            brief,
            history
        )

        draft.metrics = metrics
        draft.score = metrics["final_score"]
        draft.clip_score = metrics["clip"]
        draft.follower_score = metrics["follower_score"]
        draft.profile_visit_probability = metrics["profile_visit_probability"]
        draft.follow_probability = metrics["follow_probability"]
        draft.image_path = image_path
        draft.image_prompt = build_image_prompt(
            brief,
            draft.text
        )

        candidates.append(
            CandidatePair(
                brief=brief,
                draft=draft,
                final_score=metrics["final_score"]
            )
        )

    return sorted(
        candidates,
        key=lambda x: x.final_score,
        reverse=True
    )


def select_best(
    trends,
    history,
    out_dir
):

    best = None

    for trend in trends[:settings.topics_per_run]:

        candidates = generate_candidates(
            trend,
            history,
            out_dir
        )

        if not candidates:
            continue

        candidate = candidates[0]

        if best is None:
            best = candidate
        elif candidate.final_score > best.final_score:
            best = candidate

    return best


def update_history(
    history,
    best,
    publish_result
):

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

    history = append_history(
        history,
        record,
        best.draft.text
    )

    return history


def run(
    dry_run=False
):

    history = load_history()

    trends = fetch_trends(
        limit=max(
            10,
            settings.topics_per_run * 2
        )
    )

    out_dir = (
        settings.output_dir
        / datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    best = select_best(
        trends,
        history,
        out_dir
    )

    if best is None:
        return {
            "ok": False,
            "reason": "No valid candidate produced"
        }

    if (
    best.final_score < settings.publish_threshold
    and best.draft.follow_probability < 60
    and best.draft.profile_visit_probability < 60
):
    return {
        "ok": False,
        "reason": (
            f"Rejected: "
            f"score={best.final_score}, "
            f"follow={best.draft.follow_probability}, "
            f"profile={best.draft.profile_visit_probability}"
        )
    }

    publish_result = {
        "published": False,
        "dry_run": dry_run
    }

    if not dry_run:

        result = post_to_linkedin(
            best.draft.text,
            image_path=best.draft.image_path
        )

        publish_result = result.to_dict()

    history = update_history(
        history,
        best,
        publish_result
    )

    save_history(history)

    runs = load_runs()

    run_record = RunRecord(
        run_id=out_dir.name,
        created_at=_utc_now(),
        trend=best.brief.to_dict(),
        brief=best.brief.to_dict(),
        best_candidate=best.to_dict(),
        publish_result=publish_result,
        metrics=best.draft.metrics,
        notes=[]
    )

    runs.append(
        run_record.to_dict()
    )

    save_runs(runs)

    return {
        "ok": True,
        "topic": best.brief.topic,
        "final_score": best.final_score,
        "published": publish_result.get(
            "published",
            False
        ),
        "text": best.draft.text,
        "image_path": best.draft.image_path,
    }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run",
        action="store_true"
    )

    args = parser.parse_args()

    result = run(
        dry_run=args.dry_run
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
