import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "deepseek/deepseek-chat-v3-0324:free"


def generate_content(article):

    prompt = f"""
    You are a top AI founder and LinkedIn creator.

    Based on this news:

    TITLE:
    {article['title']}

    DESCRIPTION:
    {article['description']}

    Return ONLY valid JSON.

    Format:

    {{
      "linkedin_post": "...",
      "image_prompt": "..."
    }}

    linkedin_post:
    - strong hook
    - founder insight
    - future prediction
    - CTA
    - hashtags

    image_prompt:
    - cinematic
    - futuristic
    - hyper realistic
    - startup vibe
    - linkedin professional style
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response.choices[0].message.content

    text = text.replace("```json", "").replace("```", "")

    data = json.loads(text)

    return data