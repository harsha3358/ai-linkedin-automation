import os
import requests

from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

AI_KEYWORDS = [
    "AI",
    "OpenAI",
    "Gemini",
    "Anthropic",
    "Claude",
    "GPT",
    "LLM",
    "AI startup",
    "AI agents",
    "artificial intelligence",
    "machine learning",
    "automation",
    "Cursor",
    "Perplexity",
    "DeepMind",
    "Midjourney"
]


def is_ai_article(article):

    combined_text = f"""
    {article.get('title', '')}
    {article.get('description', '')}
    """

    combined_text = combined_text.lower()

    return any(
        keyword.lower() in combined_text
        for keyword in AI_KEYWORDS
    )


def fetch_ai_news():

    url = (
        "https://newsapi.org/v2/everything?"
        "q=AI OR OpenAI OR Gemini OR Anthropic OR GPT"
        "&language=en"
        "&sortBy=publishedAt"
        "&pageSize=25"
        f"&apiKey={NEWS_API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = data.get("articles", [])

    filtered_articles = [
        article
        for article in articles
        if is_ai_article(article)
    ]

    return filtered_articles[:10]
