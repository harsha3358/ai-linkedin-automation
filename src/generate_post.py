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
    "Most people still don’t understand what AI is actually changing.",
    "The biggest AI shift is not what most founders think.",
    "AI is changing how companies work faster than people realize.",
    "Most startups are using AI completely wrong.",
    "The next generation of companies will operate very differently.",
    "Most people think AI is just another tool.",
    "The scary part about AI is not the models.",
    "Most companies are still treating AI like a side feature.",
    "The AI companies winning right now are doing one thing differently.",
    "AI is quietly changing how work happens."
]

SARCASTIC_LINES = [
    "Some startups now have more AI tools than actual workflows.",
    "Apparently adding 'AI-powered' to the homepage is still considered strategy.",
    "Some founders automate everything except decision making.",
    "A lot of companies bought AI tools before fixing basic operations.",
    "Some startups now spend more on dashboards than product clarity.",
    "Half the startup ecosystem is workflow automation wearing sneakers.",
    "Some companies now use AI to summarize meetings that should not have existed.",
    "Many teams are moving faster now. Not always in the correct direction.",
    "Some founders are scaling confusion faster than product-market fit.",
    "AI agents are starting to sound more organized than some teams."
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
You are an elite LinkedIn creator writing for:
- students
- startup founders
- workers
- developers
- internet-native people

The writing MUST feel:
- simple
- smart
- easy to understand
- emotional
- highly readable
- modern
- creator-native

VERY IMPORTANT:

The post should:
- NOT feel corporate
- NOT feel robotic
- NOT feel AI-generated
- NOT feel text-heavy
- NOT feel like an article

The post SHOULD:
- feel like a creator explaining something important
- use short paragraphs
- use spacing beautifully
- use emotional pacing
- use conversational language
- be easy enough for anyone to understand

IMPORTANT STRUCTURE:

1. Strong hook
2. Explain what happened
3. Explain why it matters
4. Explain real-world impact
5. Add one subtle funny observation
6. End with an interesting thought

VERY IMPORTANT:

The post should:
- feel human
- feel modern
- feel emotionally engaging
- feel visually beautiful on LinkedIn

WORD COUNT:
- minimum 200 words
- maximum 350 words

VERY IMPORTANT FOR VISUALS:

Generate:
- visual_scene
- visual_emotion
- visual_style
- image_prompt

The image should feel like:
"a visual extension of the post"

TOPIC:
{article['title']}

DESCRIPTION:
{article['description']}

HOOK:
{hook}

FUNNY OBSERVATION:
{sarcastic_line}

Think step by step before writing.

Return ONLY valid JSON.

FORMAT:
{{
    "linkedin_post": "...",
    "visual_scene": "...",
    "visual_emotion": "...",
    "visual_style": "...",
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

Most people think AI is replacing jobs.

That’s not the real shift.

AI is replacing:
slow workflows.

That changes how companies operate.

Small teams can now do work that previously needed:
• bigger teams
• more meetings
• more manual operations

This is why AI-native startups are growing differently.

They move faster.

They test ideas faster.

They automate repetitive work earlier.

Funny part?

{sarcastic_line}

The companies learning this shift early will probably operate very differently over the next few years.

That’s the real AI disruption.

#AI #Startups #Technology
""",

        "visual_scene": """
small startup team using AI systems,
modern workspace,
people working with AI tools,
startup founder energy
""",

        "visual_emotion": """
modern,
exciting,
slightly chaotic,
internet-native,
emotionally engaging
""",

        "visual_style": """
cinematic creator thumbnail,
Gen Z startup aesthetic,
pastel colors,
minimal clean composition
""",

        "image_prompt": """
AI startup workflow automation,
modern creator-style social visual,
startup founder culture,
internet-native storytelling
"""
    }
