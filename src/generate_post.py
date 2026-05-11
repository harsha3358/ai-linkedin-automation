import os
import json
import time

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY missing")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

MODELS = [
    "openai/gpt-3.5-turbo",
    "meta-llama/llama-3-8b-instruct"
]


def safe_json_parse(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}") + 1

    text = text[start:end]

    return json.loads(text)


def fallback_content(article):

    return {
        "linkedin_post": f"""
AI startups are moving differently now.

{article['title']}

The biggest shift?

Small teams now have enterprise-level leverage using AI.

The next generation of founders won't build bigger teams.

They'll build smarter systems.

We're entering the AI-native era.

What workflow has AI replaced for you recently?

#AI #Startups #ArtificialIntelligence #FutureOfWork #Automation
""",

        "image_prompt": """
futuristic AI startup workspace,
cyberpunk founder aesthetics,
Gen Z startup energy,
cinematic neon lighting,
hyper realistic,
ultra detailed,
AI-native future world,
professional LinkedIn visual
"""
    }


def generate_content(article):

    prompt = f"""
You are a viral AI founder creating LinkedIn content.

Audience:
- Gen Z
- Gen Alpha
- startup founders
- AI builders

STYLE:
- futuristic
- bold
- internet-native
- concise
- emotional
- viral
- highly engaging

NEWS TITLE:
{article['title']}

NEWS DESCRIPTION:
{article['description']}

Return ONLY valid JSON.

FORMAT:
{{
  "linkedin_post": "...",
  "image_prompt": "..."
}}
"""

    for model in MODELS:

        try:

            print(f"Trying model: {model}")

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                timeout=60
            )

            text = response.choices[0].message.content

            data = safe_json_parse(text)

            return data

        except Exception as e:

            print(f"Model failed: {model}")
            print(str(e))

            time.sleep(10)

    print("Using fallback content generator...")

    return fallback_content(article)