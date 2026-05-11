import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_TOKEN"),
)

def generate_image(prompt):

    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-dev",
    )

    os.makedirs("assets", exist_ok=True)

    image_path = "assets/post.png"

    image.save(image_path)

    return image_path