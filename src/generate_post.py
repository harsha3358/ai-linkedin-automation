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

HOOKS = [
    "Most people are underestimating this AI shift.",
    "This AI update could quietly reshape entire industries.",
    "Founders should pay attention to this carefully.",
    "This is where AI becomes economically dangerous.",
    "AI companies are moving faster than regulators can react.",
    "The gap between AI-native companies and traditional companies is widening.",
    "This might become one of the biggest AI shifts of the year."
]

CTAS = [
    "Would you trust AI systems with critical business decisions?",
    "What part of your workflow has AI already replaced?",
    "Do you think companies are adopting AI too aggressively?",
    "Would you use this technology inside your company?",
    "Which industry gets disrupted first by this?"
]

CONTROVERSIAL_ANGLES = [
    "AI may reduce the need for large operational teams.",
    "Many current white-collar workflows may disappear within this decade.",
    "AI-native startups could outperform traditional enterprises with much smaller teams.",
    "Companies refusing AI adoption may struggle to compete globally.",
    "The future workforce may value adaptability over specialization."
]


def safe_json_parse(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}") + 1

    text = text[start:end]

    return json.loads(text)


def fallback_content(article):

    hook = random.choice(HOOKS)
    cta = random.choice(CTAS)
    controversial = random.choice(CONTROVERSIAL_ANGLES)

    return {
        "linkedin_post": f"""
{hook}

Today’s AI update:

{article['title']}

What is happening?

{article['description']}

Why does this matter?

AI systems are increasingly becoming operational infrastructure instead of optional tools.

Real-world uses:
• Workflow automation
• Faster product execution
• Customer support scaling
• Research acceleration
• Internal productivity systems

Pros:
• Faster execution
• Lower costs
• Better scalability
• Smaller but stronger teams

Cons:
• Job displacement concerns
• Data privacy risks
• AI hallucinations
• Overdependence on automation

Founder perspective:

{controversial}

Funny observation:

Some startups now have more AI agents than actual employees.

Real-world impact:

Businesses adopting AI early are building operational leverage much faster than traditional companies.

The next generation of companies may look fundamentally different from today's enterprises.

{cta}

#AI #ArtificialIntelligence #Technology #Startups #FutureOfWork
""",

        "image_prompt": """
funny sarcastic AI meme scene,
Gen Z internet humor,
light pastel color palette,
soft neon aesthetic,
minimal clean background,
modern startup chaos,
sleep deprived founders,
AI replacing entire departments humorously,
cinematic but funny,
viral social media style,
high engagement visual,
Twitter meme energy,
LinkedIn friendly humor,
ultra detailed,
high quality,
internet-native aesthetic,
light colors,
soft blue,
soft purple,
soft pink,
modern meme composition,
funny but professional
""",

        "carousel_ideas": [
            "Slide 1: Strong Hook",
            "Slide 2: What happened",
            "Slide 3: Why it matters",
            "Slide 4: Real-world uses",
            "Slide 5: Pros",
            "Slide 6: Cons",
            "Slide 7: Founder perspective",
            "Slide 8: Funny observation",
            "Slide 9: CTA"
        ],

        "meme_idea": "AI replacing 20 tabs, 4 interns, and 3 meetings with one prompt.",

        "trend_score": random.randint(7, 10)
    }


def generate_content(article):

    hook = random.choice(HOOKS)
    cta = random.choice(CTAS)
    controversial = random.choice(CONTROVERSIAL_ANGLES)

    prompt = f"""
You are an elite AI founder and viral LinkedIn strategist.

Your audience:
- Gen Z
- Gen Alpha
- startup founders
- AI builders
- tech professionals

NEVER use the emoji 🚀.

Write content that feels:
- intelligent
- funny
- sarcastic
- internet-native
- lightly chaotic
- Gen Z readable
- founder-level
- emotionally engaging
- meme-aware
- highly shareable

The humor should feel subtle and smart.

Do NOT sound cringe.

Use:
- sarcastic observations
- funny founder pain points
- internet humor
- modern startup culture references

Avoid:
- boomer humor
- excessive emojis
- childish jokes
- corporate tone

POST STRUCTURE:

1. Strong hook
2. Explain WHAT happened
3. Explain USES
4. Explain PROS
5. Explain CONS
6. Founder perspective
7. Real-world impact
8. Engagement CTA
9. Include one funny/sarcastic observation

Include:
- one controversial insight
- one future prediction
- one strong founder observation

HOOK:
{hook}

CTA:
{cta}

CONTROVERSIAL ANGLE:
{controversial}

NEWS TITLE:
{article['title']}

NEWS DESCRIPTION:
{article['description']}

Return ONLY valid JSON.

FORMAT:
{{
  "linkedin_post": "...",
  "image_prompt": "...",
  "carousel_ideas": ["..."],
  "meme_idea": "...",
  "trend_score": 9
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