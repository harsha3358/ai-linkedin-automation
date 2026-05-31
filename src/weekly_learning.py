from collections import Counter


def analyze_history(history):
    posts = history.get("posts", [])

    topics = []
    audiences = []
    voices = []

    for post in posts:
        topics.append(post.get("topic"))
        audiences.append(post.get("audience"))
        voices.append(post.get("voice"))

    return {
        "best_topics": Counter(topics).most_common(5),
        "best_audiences": Counter(audiences).most_common(5),
        "best_voices": Counter(voices).most_common(5),
    }


def get_recommendations(history):
    stats = analyze_history(history)

    return {
        "topic": stats["best_topics"][0][0] if stats["best_topics"] else None,
        "audience": stats["best_audiences"][0][0] if stats["best_audiences"] else None,
        "voice": stats["best_voices"][0][0] if stats["best_voices"] else None,
    }