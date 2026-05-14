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
Google was behind in AI for years.

Now they're suddenly shipping models every week.

Today's example?

{article['title']}

Here’s what’s happening.

{article['description']}

This is important because AI companies are no longer competing on:
• model quality only

Now they're competing on:
• speed
• ecosystem
• workflow integration
• distribution

And honestly?

Most companies still think AI means “ChatGPT wrapper + dark mode”.

Meanwhile AI-native startups are building entire workflows with agents.

That changes everything.

Funny part?

Some founders now spend more time talking to AI than their actual employees.

The scary part is...

The AI tools are usually faster.

The next few years won't just change software.

They'll change how companies operate entirely.

#AI #ArtificialIntelligence #Startups #Technology
""",

        "image_prompt": """
viral Gen Z AI meme visual,
pastel colors,
funny startup humor,
AI replacing interns,
modern internet culture aesthetic,
clean cinematic composition,
soft purple and blue colors,
founder stress meme,
AI agents everywhere,
high engagement social media visual,
minimal but emotional,
ultra modern aesthetic,
tech meme energy,
professional but funny,
high-detail digital art
"""
    }


def generate_content(article):

    prompt = f"""
You are writing LinkedIn posts EXACTLY in this style:

- Vaibhav Sisinty
- viral founder creators
- internet-native storytelling
- Gen Z formatting
- short punchy lines
- conversational pacing
- dramatic curiosity
- smart sarcasm
- emotional momentum

VERY IMPORTANT:

The post should NOT feel like:
- an article
- a blog
- a report
- AI summary
- corporate analysis

It should feel like:
- a founder talking naturally
- a viral AI knowledge pill
- internet-native storytelling
- high-retention content

STYLE RULES:

- short lines only
- 1 sentence paragraphs
- high readability
- suspense pacing
- curiosity loops
- founder commentary
- subtle sarcasm
- emotional flow
- highly shareable

AVOID:
- huge paragraphs
- corporate tone
- cringe motivation
- excessive hashtags
- excessive emojis
- generic summaries

IMPORTANT STRUCTURE:

1. Strong hook
2. Explain WHAT happened
3. Explain WHY it's important
4. Explain REAL-WORLD IMPACT
5. Add one funny/sarcastic founder observation
6. End with an interesting thought/question

The content should feel like:
"daily AI knowledge pill for founders"

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
