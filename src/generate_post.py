import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

print("OPENROUTER KEY FOUND:", API_KEY is not None)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

MODEL = "meta-llama/llama-3.3-70b-instruct:free"


def generate_content(article):

    prompt = f"""
You are a viral AI founder and futuristic internet creator.

Your audience is:
- Gen Z
- Gen Alpha
- startup founders
- AI builders
- creators
- ambitious students

Write like:
- a smart AI founder
- internet-native
- futuristic
- emotionally engaging
- highly shareable

DO NOT sound:
- corporate
- robotic
- generic
- like a consultant

STYLE RULES:
- short punchy lines
- visually spaced formatting
- emotionally charged hooks
- curiosity-driven
- startup energy
- futuristic thinking
- easy to skim
- high engagement

POST STRUCTURE:
1. Strong viral hook
2. Why this matters
3. Future prediction
4. Emotional insight
5. CTA
6. Hashtags

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

linkedin_post:
- should feel viral
- should feel modern
- should trigger curiosity
- should feel like future tech culture
- should contain short spaced paragraphs

image_prompt:
- futuristic AI startup world
- Gen Z aesthetics
- cinematic lighting
- neon atmosphere
- hyper realistic
- ambitious founder energy
- social media optimized
- ultra detailed
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response.choices[0].message.content

    print("\nRAW MODEL OUTPUT:\n")
    print(text)

    text = text.replace("```json", "").replace("```", "")

    data = json.loads(text)

    return data


if __name__ == "__main__":

    sample_article = {
        "title": "OpenAI launches next-generation autonomous AI agents",
        "description": "OpenAI introduced powerful autonomous AI agents capable of handling complex workflows independently."
    }

    result = generate_content(sample_article)

    print("\nFINAL OUTPUT:\n")
    print(json.dumps(result, indent=2))