import os
import json
import time

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

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


def generate_content(article):

    prompt = f"""
You are an elite AI creator writing viral founder-style LinkedIn posts.

STYLE:
- Vaibhav Sisinty
- Gen Z founder energy
- internet-native storytelling
- curiosity hooks
- short punchy lines
- emotional pacing
- smart sarcasm
- highly readable
- modern startup humor

VERY IMPORTANT:

The post MUST:
- explain the AI update clearly
- explain why it matters
- explain real-world impact
- feel like insider AI commentary
- feel creator-native
- feel modern and human

DO NOT:
- sound corporate
- sound like a blog
- sound like finance news
- sound like ChatGPT summaries
- write long paragraphs
- use cringe engagement bait

WRITE LIKE:
- a founder obsessed with AI
- someone explaining the future casually
- internet-native AI storytelling

VERY IMPORTANT:

Generate BOTH:
1. the LinkedIn post
2. the cinematic image concept

The IMAGE PROMPT should:
- match the emotional tone of the post
- feel cinematic
- feel Gen Z
- feel internet-native
- feel funny/sarcastic
- use pastel colors
- feel modern
- feel highly shareable
- NOT feel generic cyberpunk

TOPIC:
{article['title']}

DESCRIPTION:
{article['description']}

RETURN JSON ONLY

FORMAT:
{{
    "linkedin_post": "...",
    "image_prompt": "..."
}}
"""

    for model in MODELS:

        try:

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

            return safe_json_parse(text)

        except Exception as e:

            print(str(e))

            time.sleep(5)

    return {
        "linkedin_post": f"""
AI companies are moving insanely fast right now.

{article['title']}

Most people still think AI is just:
“chatbot + productivity.”

Meanwhile startups are replacing entire workflows with agents.

That changes everything.
""",

        "image_prompt": """
funny AI startup meme,
pastel aesthetic,
Gen Z humor,
modern founder chaos,
light colors,
soft purple tones,
internet-native visual,
cinematic but funny,
AI workflow overload,
minimal clean composition
"""
    }
