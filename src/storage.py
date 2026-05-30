from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import settings


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_history() -> Dict[str, Any]:
    payload = _read_json(settings.history_file, default={})
    if not isinstance(payload, dict):
        payload = {}
    payload.setdefault("posts", [])
    payload.setdefault("topics", [])
    payload.setdefault("signatures", [])
    payload.setdefault("cta_history", [])
    payload.setdefault("voice_history", [])
    payload.setdefault("image_styles", [])
    return payload


def save_history(history: Dict[str, Any]) -> None:
    _write_json(settings.history_file, history)


def load_runs() -> List[Dict[str, Any]]:
    payload = _read_json(settings.runs_file, default=[])
    return payload if isinstance(payload, list) else []


def save_runs(runs: List[Dict[str, Any]]) -> None:
    _write_json(settings.runs_file, runs)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch.isspace())
    return " ".join(text.split())


def text_signature(text: str) -> str:
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def recent_texts(history: Dict[str, Any], limit: int = 20) -> List[str]:
    posts = history.get("posts", [])
    items = []
    for post in posts[-limit:]:
        if isinstance(post, dict):
            txt = post.get("text", "")
            if txt:
                items.append(txt)
    return items


def recent_signatures(history: Dict[str, Any], limit: int = 100) -> List[str]:
    sigs = history.get("signatures", [])
    return list(sigs[-limit:]) if isinstance(sigs, list) else []


def append_history(history: Dict[str, Any], record: Dict[str, Any], text: str) -> Dict[str, Any]:
    history.setdefault("posts", [])
    history.setdefault("topics", [])
    history.setdefault("signatures", [])
    history.setdefault("cta_history", [])
    history.setdefault("voice_history", [])
    history.setdefault("image_styles", [])
    history["posts"].append(record)
    history["signatures"].append(text_signature(text))
    return history


def dedupe_keep_order(items: List[Any], key_fn=None) -> List[Any]:
    seen = set()
    out = []
    for item in items:
        key = key_fn(item) if key_fn else item
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out