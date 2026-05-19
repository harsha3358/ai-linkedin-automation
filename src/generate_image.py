import os
import base64

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

client = OpenAI(
    api_key=OPENAI_API_KEY
)


def generate_image(prompt):

    enhanced_prompt = f"""
Create a viral LinkedIn creator-style image.

STYLE:
- Gen Z founder aesthetic
- cinematic composition
- pastel colors
- startup meme energy
- subtle sarcasm
- modern internet-native design
- highly shareable
- minimal clean composition
- NOT cyberpunk
- NOT generic AI art

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

        print("GPT image generation failed")
        print(str(e))

        return None
