from scrape_news import fetch_ai_news
from rank_news import rank_articles
from generate_post import generate_content
from generate_image import generate_image
from post_linkedin import post_to_linkedin


def run_pipeline():

    print("Fetching latest AI news...")

    articles = fetch_ai_news()

    if not articles:

        print("No AI articles found.")
        return

    print("Ranking news...")

    best_article = rank_articles(articles)

    print("Best Article:")
    print(best_article)

    print("Generating creator-style content...")

    content = generate_content(best_article)

    linkedin_post = content["linkedin_post"]

    visual_scene = content.get(
        "visual_scene",
        ""
    )

    visual_emotion = content.get(
        "visual_emotion",
        ""
    )

    visual_style = content.get(
        "visual_style",
        ""
    )

    image_prompt = f"""
SCENE:
{visual_scene}

EMOTION:
{visual_emotion}

STYLE:
{visual_style}

BASE PROMPT:
{content['image_prompt']}
"""

    print("\nGenerated Post:\n")
    print(linkedin_post)

    print("\nGenerating creator-style image...\n")

    image_path = generate_image(image_prompt)

    if image_path:

        print("Posting with image...\n")

        post_to_linkedin(
            linkedin_post,
            image_path
        )

        print("LinkedIn post published successfully.")

    else:

        print("Image generation failed.")

        print("Posting text-only content...\n")

        post_to_linkedin(
            linkedin_post
        )

        print("LinkedIn text post published successfully.")


if __name__ == "__main__":
    run_pipeline()
