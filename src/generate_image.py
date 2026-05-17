import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)


def generate_image(prompt):

    enhanced_prompt = f"""
{prompt}

STYLE REQUIREMENTS:
- Gen Z aesthetic
- pastel colors
- soft lighting
- modern meme culture
- cinematic composition
- emotionally expressive
- startup founder energy
- internet-native humor
- minimal clean design
- high engagement social media style
- highly detailed
- modern visual storytelling
- soft blue and purple palette
- NOT dark cyberpunk
- NOT generic AI art
"""

    try:

        image = client.text_to_image(
            enhanced_prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )

        os.makedirs("assets", exist_ok=True)

        image_path = "assets/post.png"

        image.save(image_path)

        return image_path

    except Exception as e:

        print("Image generation failed")
        print(str(e))

        return None
