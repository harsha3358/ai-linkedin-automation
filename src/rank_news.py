def rank_articles(articles):

    filtered = []

    for article in articles:

        title = article.get("title")
        description = article.get("description")
        url = article.get("url")

        if not title:
            continue

        if not description:
            continue

        if len(description.strip()) < 40:
            continue

        if not url:
            continue

        blocked_domains = [
            "consent.yahoo",
            "removed",
            "privacy",
            "signin",
            "login"
        ]

        if any(domain in url for domain in blocked_domains):
            continue

        filtered.append(article)

    if not filtered:
        return {
            "title": "AI is transforming startup execution",
            "description": "AI-native startups are moving faster than traditional businesses by automating workflows, content, operations, and product development.",
            "url": "https://openai.com"
        }

    return filtered[0]