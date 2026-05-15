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

This matters because AI companies are no longer competing only on model quality.

Now they're competing on:
• speed
• ecosystem
• workflow integration
• distribution

Which changes everything.

Most companies still think AI means:
“ChatGPT + dark mode + productivity tweet.”

Meanwhile AI-native startups are building full workflows with agents.

Funny part?

Some startups now spend enough on GPU compute to qualify as climate influencers.

Real-world impact?

The companies learning AI workflows today may operate completely differently from traditional companies within a few years.

AI is slowly shifting from:
tool → infrastructure.

And that changes how businesses scale.

Curious to see how founders like Sam Altman and Sundar Pichai push this even further.

#AI #ArtificialIntelligence #Startups #Technology #FutureOfWork
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
high-detail digital art,
eco-friendly futuristic office,
light colors,
sarcastic startup energy
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

IMPORTANT STRUCTURE:

1. Strong hook
2. Explain WHAT happened
3. Explain WHY it's important
4. Explain REAL-WORLD IMPACT
5. Add one funny/sarcastic founder observation
6. Mention relevant founders naturally
7. End with an interesting thought/question
8. Add domain-specific hashtags

IMPORTANT:

The humor should feel:
- playful
- founder-native
- internet-smart
- environmentally aware
- lightly sarcastic
- socially aware

Examples:
- "Some startups now consume enough GPU power to heat small countries."
- "AI agents are becoming cheaper than SaaS subscriptions."
- "Carbon emissions are rising but at least the pitch decks look futuristic."

Avoid:
- offensive humor
- insulting founders personally
- cringe meme spam
- edgy jokes

The content should feel like:
"daily AI knowledge pill for founders"

TOPIC:
{article['title']}

DESCRIPTION:
{article['description']}

Also include:
- relevant founder mentions if applicable
- company mentions naturally
- domain-specific hashtags

Examples:
- OpenAI news → Sam Altman
- Google AI → Sundar Pichai
- Anthropic → Dario Amodei
- Meta AI → Mark Zuckerberg

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
