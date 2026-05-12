import os
import json
import random
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

FUNNY_LINES = [
    "Some companies now have more AI agents than employees.",
    "At this point the intern is just supervising AI tools.",
    "Half the startup ecosystem is now basically prompt engineering with caffeine.",
    "Traditional workflows are slowly becoming historical artifacts.",
    "People spent years learning Excel just for AI to press tab once.",
    "Meetings are becoming expensive compared to one good AI workflow."
]


def safe_json_parse(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}") + 1

    text = text[start:end]

    return json.loads(text)


def fallback_content(article):

    funny_line = random.choice(FUNNY_LINES)

    return {
        "linkedin_post": f"""
Today’s AI update:

{article['title']}

What happened?

{article['description']}

Why this matters:

AI companies are no longer competing only on model quality.

They are competing on:
• speed
• distribution
• workflow integration
• operational leverage

Real-world uses:
• automating repetitive work
• faster research
• content generation
• customer support
• software development assistance
• internal business automation

Pros:
• significantly faster execution
• lower operational costs
• smaller but more productive teams
• faster experimentation cycles

Cons:
• AI hallucinations
• overdependence on automation
• privacy concerns
• increasing pressure on traditional jobs

Founder perspective:

The companies learning AI workflows today may operate very differently from companies built even 5 years ago.

Funny observation:

{funny_line}

Real-world impact:

AI is slowly shifting from “tool” to “infrastructure”.

That changes how startups scale, hire, build products, and compete globally.

#AI #ArtificialIntelligence #Technology #Startups #FutureOfWork
""",

        "image_prompt": """
funny sarcastic AI workplace,
Gen Z internet humor,
light pastel aesthetic,
soft neon colors,
modern startup meme energy,
founders overwhelmed by AI tools,
minimal clean composition,
cinematic but funny,
high engagement social media visual,
professional but sarcastic,
soft blue and purple tones,
modern internet-native visual style
"""
    }


def generate_content(article):

    funny_line = random.choice(FUNNY_LINES)

    prompt = f"""
You are a highly intelligent AI founder writing informative LinkedIn posts.

IMPORTANT:

The post MUST:
- explain the AI news clearly
- explain what the technology/model/company does
- explain real-world uses
- explain pros and cons
- explain real-world impact
- include one subtle sarcastic/funny observation
- sound modern and intelligent
- avoid cringe engagement bait
- avoid fake motivational content
- avoid random unrelated statements
- avoid excessive emojis
- NEVER use the 🚀 emoji

The humor should feel:
- subtle
- internet-native
- founder humor
- slightly sarcastic
- smart

NOT:
- childish
- meme spam
- corporate
- exaggerated

POST STRUCTURE:

1. Explain the AI update/topic first
2. Explain what it actually does
3. Explain real-world uses
4. Explain pros
5. Explain cons
6. Explain founder/business impact
7. Add one funny observation naturally
8. End professionally

IMPORTANT:
The post must feel educational and insightful first.
Humor is secondary.

FUNNY OBSERVATION:
{funny_line}

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
