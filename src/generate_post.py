import os
import json
import random
import time

from openai import OpenAI
from dotenv import load_dotenv

from validation import (
    validate_post,
    ensure_not_paragraph_heavy,
    has_good_spacing,
    final_cleanup
)

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
    "AI startups are making the same mistake SaaS startups made in 2018.",
    "The market rewards clarity more than complexity.",
    "Most AI startups are accidentally becoming feature lists.",
    "AI is changing how companies operate much faster than people realize.",
    "The next generation of startups will look operationally different.",
    "Most founders still underestimate workflow automation.",
    "AI-native startups are scaling differently already.",
    "The real AI disruption is operational, not visual.",
    "Most companies still use AI like a toy."
]

SARCASTIC_LINES = [
    "Some startups now have more AI tools than paying customers.",
    "Apparently adding 'AI-powered' to the homepage is still considered strategy.",
    "Half the startup ecosystem is now workflow automation wearing sneakers.",
    "Some founders pivot so often their landing page needs version control.",
    "Many startups now spend more money on GPUs than marketing.",
    "The AI agents are starting to sound more organized than the teams using them.",
    "Some companies automated everything except decision making.",
    "AI is removing repetitive work faster than meetings.",
    "Startups are discovering automation after hiring 14 dashboards.",
    "Some founders are scaling confusion faster than product-market fit."
]

MEMORY_FILE = "src/content_memory.json"


def load_memory():

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=2)


def get_unique_item(items, used_items):

    available = [
        item for item in items
        if item not in used_items
    ]

    if not available:

        used_items.clear()

        available = items.copy()

    return random.choice(available)


def safe_json_parse(text):

    text = text.replace("```json", "")
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}") + 1

    text = text[start:end]

    return json.loads(text)


def generate_content(article):

    memory = load_memory()

    hook = get_unique_item(
        HOOKS,
        memory["used_hooks"]
    )

    sarcastic_line = get_unique_item(
        SARCASTIC_LINES,
        memory["used_jokes"]
    )

    memory["used_hooks"].append(hook)
    memory["used_jokes"].append(sarcastic_line)

    save_memory(memory)

    prompt = f"""
You are an elite LinkedIn founder creator.

Write EXACTLY like:
- founder creators
- startup operators
- internet-native builders

The writing should feel:
- direct
- smart
- tactical
- creator-native
- human
- highly readable
- emotionally engaging

DO NOT:
- sound corporate
- sound robotic
- summarize mechanically
- write huge paragraphs
- sound motivational
- use cringe engagement bait

IMPORTANT FORMATTING RULES:

- short paragraphs only
- maximum readability
- breathing space between thoughts
- one idea per paragraph
- short punchy pacing
- conversational flow

VERY IMPORTANT:

The post should:
- feel creator-native
- feel insightful
- feel like insider founder commentary
- explain ONE important strategic insight
- create curiosity
- create retention

The post MUST look visually beautiful on LinkedIn.

Add spacing naturally.

Add subtle sarcasm naturally.

DO NOT:
- overuse hashtags
- overuse emojis
- use walls of text

TOPIC:
{article['title']}

DESCRIPTION:
{article['description']}

HOOK:
{hook}

SARCASTIC OBSERVATION:
{sarcastic_line}

Think step by step before writing.

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

            data = safe_json_parse(text)

            post = final_cleanup(
                data["linkedin_post"]
            )

            valid = (
                validate_post(post)
                and ensure_not_paragraph_heavy(post)
                and has_good_spacing(post)
            )

            if valid:

                data["linkedin_post"] = post

                return data

        except Exception as e:

            print(str(e))

            time.sleep(5)

    return {
        "linkedin_post": f"""
{hook}

Most startups think AI gives them leverage.

Sometimes it just gives them more noise.

The real advantage isn’t:
using AI.

It’s building workflows around it.

That’s the shift most companies still miss.

AI-native startups are operating differently already.

Smaller teams.

Faster execution.

Less operational drag.

Funny part?

{sarcastic_line}

The companies learning this early will move differently over the next few years.

That’s the real disruption.

#AI #Startups #Founders
""",

        "image_prompt": """
modern AI founder workspace,
Gen Z startup aesthetic,
light pastel colors,
cinematic but funny,
internet-native visual storytelling,
soft blue and purple palette,
modern creator energy,
highly shareable social media visual,
minimal clean composition,
subtle startup sarcasm,
founder chaos aesthetic,
professional but relatable
"""
    }
