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
Google was behind on AI for years.

Now they’re shipping models every few weeks.

Today’s example?

{article['title']}

Here’s why this matters.

AI companies are no longer competing only on:
• model quality

Now they compete on:
• speed
• ecosystem
• workflow integration
• distribution

That changes everything.

Most startups still use AI like:
“write me a caption”.

Meanwhile AI-native companies are replacing entire workflows with agents.

Funny part?

Some founders now spend more time talking to AI than their own teams.

And honestly...

the AI replies faster.

The next few years won’t just change software.

They’ll change how companies operate entirely.

#AI #ArtificialIntelligence #Startups #Technology
""",

        "image_prompt": """
funny AI startup meme,
Gen Z internet humor,
light pastel colors,
soft blue and purple aesthetic,
founders overwhelmed by AI tools,
cinematic meme composition,
internet-native humor,
AI replacing traditional workflows,
minimal clean visual,
high engagement social media image,
modern startup culture,
professional but funny,
viral AI visual
"""
    }


def generate_content(article):

    prompt = f"""
You are writing viral LinkedIn posts EXACTLY like top AI creator founders.

STYLE REFERENCE:
- Vaibhav Sisinty style
- AI insider storytelling
- short punchy lines
- dramatic pacing
- curiosity hooks
- internet-native formatting

VERY IMPORTANT:

DO NOT:
- sound corporate
- sound like news summary
- sound like finance content
- sound motivational
- sound like marketing copy
- write paragraphs
- use generic engagement bait

WRITE LIKE:
- an AI founder
- someone obsessed with AI
- internet-native creator
- modern startup operator

FORMAT RULES:
- short lines only
- max 1-2 sentences per paragraph
- easy readability
- suspense pacing
- emotional momentum
- subtle sarcasm
- smart founder humor

VERY IMPORTANT:

ONLY talk about:
- AI
- startups
- automation
- models
- AI products
- AI agents
- AI workflows
- AI future

IGNORE:
- stock market news
- ETFs
- investing
- unrelated finance news

The post should feel like:
“daily AI knowledge pill for founders”

POST STRUCTURE:

1. strong hook
2. explain what happened
3. explain why it matters
4. explain real-world impact
5. funny founder observation
6. interesting ending thought

TOPIC:
{article['title']}

DESCRIPTION:
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
