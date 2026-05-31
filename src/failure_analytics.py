from datetime import datetime


def create_failure_record(
    failure_type,
    failure_reason,
    critic_feedback=""
):
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "failure_type": failure_type,
        "failure_reason": failure_reason,
        "critic_feedback": critic_feedback,
    }


def store_failure(history, record):
    history.setdefault("failures", [])
    history["failures"].append(record)

    if len(history["failures"]) > 500:
        history["failures"] = history["failures"][-500:]

    return history


def get_top_failures(history):
    failures = history.get("failures", [])

    counts = {}

    for item in failures:
        key = item.get("failure_type")

        if not key:
            continue

        counts[key] = counts.get(key, 0) + 1

    return sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )