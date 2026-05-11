import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_ai_news():

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=OpenAI OR Anthropic OR Gemini OR AI agents OR AI startup OR artificial intelligence"
        f"&language=en"
        f"&sortBy=publishedAt"
        f"&pageSize=10"
        f"&apiKey={NEWS_API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = []

    for article in data["articles"]:

        articles.append({
            "title": article["title"],
            "description": article["description"],
            "url": article["url"]
        })

    return articles