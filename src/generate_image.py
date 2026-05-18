import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

client = OpenAI(
    api_key=API_KEY
)


def generate_image(prompt):

    enhanced_prompt = f"""
Create a highly engaging LinkedIn visual.

STYLE:
- modern startup creator aesthetic
- Gen Z internet-native humor
- cinematic composition
- soft pastel colors
- minimal clean design
- emotionally expressive
- modern founder culture
- meme-aware visual storytelling
- subtle sarcasm
- highly shareable
- NOT generic AI art
- NOT cyberpunk
- NOT dark

VISUAL REQUIREMENTS:
- visually attractive
- social media optimized
- creator-style image
- modern internet aesthetic
- highly detailed
- professional but funny
- startup culture energy

SCENE:
{prompt}
"""

    try:

        response = client.images.generate(
            model="gpt-image-1",
            prompt=enhanced_prompt,
            size="1024x1024"
        )

        image_base64 = response.data[0].b64_json

        image_bytes = base64.b64decode(image_base64)

        os.makedirs("assets", exist_ok=True)

        image_path = "assets/post.png"

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        print("Image generated successfully")

        return image_path

    except Exception as e:

        print("GPT Image generation failed")
        print(str(e))

        return None
