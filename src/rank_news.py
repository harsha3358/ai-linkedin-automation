def rank_articles(articles):

    ranked = sorted(
        articles,
        key=lambda x: len(x["title"]),
        reverse=True
    )

    return ranked[0]