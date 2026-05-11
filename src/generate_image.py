import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

if not HF_TOKEN:
    raise ValueError("HF_TOKEN missing")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)


def generate_image(prompt):

    try:

        image = client.text_to_image(
            prompt,
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