import os
import time
import random
import requests
import urllib.parse


VISUAL_STYLES = [
    "modern startup meme aesthetic",
    "Gen Z creator visual",
    "internet-native startup storytelling",
    "viral LinkedIn creator image",
    "minimal founder aesthetic",
    "soft cinematic startup visual",
    "AI startup culture meme",
    "modern creator economy visual",
    "high-retention social media visual",
    "pastel creator-style composition"
]

VISUAL_MOODS = [
    "soft purple and blue tones",
    "light pastel colors",
    "clean cinematic lighting",
    "minimal clean composition",
    "emotionally expressive",
    "modern internet aesthetic",
    "professional but funny",
    "subtle sarcasm energy",
    "startup founder chaos",
    "highly shareable social media design"
]


def build_prompt(prompt):

    style = random.choice(VISUAL_STYLES)

    mood = random.choice(VISUAL_MOODS)

    enhanced_prompt = f"""
{style},
{mood},

Create a visually attractive creator-style image.

IMPORTANT:
- NOT generic AI art
- NOT cyberpunk
- NOT dark
- NOT futuristic city posters
- NOT random robots

The image should feel:
- modern
- startup-native
- internet-native
- emotionally engaging
- creator economy aesthetic
- LinkedIn creator visual
- Gen Z startup culture

The composition should:
- look clean
- look premium
- look social-media optimized
- feel highly shareable

SCENE:
{prompt}
"""

    return enhanced_prompt


def generate_image(prompt):

    try:

        enhanced_prompt = build_prompt(prompt)

        encoded_prompt = urllib.parse.quote(
            enhanced_prompt
        )

        seed = random.randint(1, 999999)

        image_url = (
            f"https://image.pollinations.ai/prompt/"
            f"{encoded_prompt}"
            f"?width=1024"
            f"&height=1024"
            f"&seed={seed}"
            f"&model=flux"
        )

        print("Generating creator-style image...")

        response = requests.get(
            image_url,
            timeout=90
        )

        if response.status_code == 200:

            os.makedirs("assets", exist_ok=True)

            image_path = "assets/post.png"

            with open(image_path, "wb") as f:
                f.write(response.content)

            print("Image generated successfully")

            return image_path

        print("Failed to generate image")

        return None

    except Exception as e:

        print("Image generation failed")
        print(str(e))

        return None
