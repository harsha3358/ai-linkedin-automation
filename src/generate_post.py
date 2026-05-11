import os
import json
import time

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

if not API_KEY.startswith("sk-or-v1-"):
    raise ValueError("Invalid OpenRouter API key")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# fallback models
MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-2-9b-it:free"
]


def try_model(model_name, prompt):

    print(f"\nTrying model: {model_name}")

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response


def generate_content(article):

    prompt = f"""
You are a viral AI founder and futuristic internet creator.

Audience:
- Gen Z
- Gen Alpha
- AI founders
- startup builders

STYLE:
- bold
- futuristic
- internet-native
- emotionally engaging
- concise
- viral
- visually spaced

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

    last_error = None

    for model in MODELS:

        try:

            response = try_model(model, prompt)

            text = response.choices[0].message.content

            print("\nRAW MODEL OUTPUT:\n")
            print(text)

            text = text.replace("```json", "")
            text = text.replace("```", "")

            data = json.loads(text)

            return data

        except Exception as e:

            print(f"\nModel failed: {model}")
            print(str(e))

            last_error = e

            time.sleep(5)

    raise last_error