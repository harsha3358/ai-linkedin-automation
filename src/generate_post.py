import os
import json
import random
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

HOOKS = [
    "Most founders waste years before realizing this.",
    "Your positioning decides your startup’s growth speed.",
    "Most startups don’t fail because of product.",
    "The market usually rewards clarity before innovation.",
    "Broad positioning quietly kills early-stage startups.",
    "Most AI startups are accidentally becoming feature lists.",
]

SARCASTIC_LINES = [
    "Some startups now have 14 AI features and still no clear customer.",
    "Apparently adding 'AI-powered' to the homepage is still considered strategy.",
    "Half the startup ecosystem is now just workflow automation wearing sneakers.",
    "Many founders are scaling confusion faster than product-market fit.",
    "Some startups pivot so often the landing page needs version control."
]


def safe_json_parse(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}") + 1

    text = text[start:end]

    return json.loads(text)


def generate_content(article):

    hook = random.choice(HOOKS)
    sarcastic_line = random.choice(SARCASTIC_LINES)

    prompt = f"""
You are writing elite LinkedIn content for startup founders.

Your style is a combination of:
- founder/operator thinking
- internet-native storytelling
- tactical startup insight
- modern creator pacing
- subtle sarcasm
- high-retention formatting

The writing should feel:
- direct
- intelligent
- experience-led
- practical
- creator-native
- emotionally engaging
- highly readable

NOT:
- motivational
- corporate
- generic
- AI-generated
- robotic
- blog-style

IMPORTANT:

This should feel like:
"a founder explaining something important after learning it the hard way."

The content must:
- sound human
- feel natural
- create curiosity
- use punchy short paragraphs
- use emotional pacing
- create tension
- explain real startup implications
- feel highly shareable

DO NOT:
- summarize news mechanically
- explain everything academically
- use generic engagement bait
- use huge paragraphs
- use excessive emojis
- sound like ChatGPT

STYLE RULES:
- one sentence paragraphs preferred
- maximum readability
- conversational flow
- suspense pacing
- tactical insights
- subtle founder humor

CONTENT FLOW:

1. Start with a powerful hook
2. Explain the real strategic insight
3. Explain why most founders miss this
4. Explain real-world startup implications
5. Add one subtle sarcastic observation naturally
6. End with a strong founder takeaway

VERY IMPORTANT:

The post should feel like:
- insider founder knowledge
- startup pattern recognition
- creator-style storytelling
- practical strategic thinking

NOT:
- generic advice
- motivational fluff
- startup clichés

TOPIC:
{article['title']}

DESCRIPTION:
{article['description']}

HOOK:
{hook}

SARCASTIC OBSERVATION:
{sarcastic_line}

Think step by step before writing.

Write a LinkedIn post under 2200 characters.

Return ONLY valid JSON.

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
{hook}

Most founders think growth problems are marketing problems.

They’re usually positioning problems.

Especially in AI.

Early-stage startups often try to target:
• everyone
• every workflow
• every industry

Which sounds ambitious.

But usually creates invisible companies.

The fastest-growing startups usually dominate:
• one painful problem
• one user type
• one workflow

before expanding.

That’s how markets remember them.

Funny part?

{sarcastic_line}

Clarity compounds faster than complexity.

Especially in crowded AI markets.

#Startups #AI #Founders
""",

        "image_prompt": """
modern AI startup founder,
minimal workspace,
Gen Z founder aesthetic,
pastel colors,
cinematic lighting,
internet-native startup humor,
founder stress energy,
subtle sarcastic visual storytelling,
modern clean composition,
soft purple and blue palette,
highly shareable social media image,
professional but relatable,
startup chaos aesthetic,
light colors,
modern creator-style visual
"""
    }
