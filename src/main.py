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

    print("Generating AI creator-style content...")

    content = generate_content(best_article)

    linkedin_post = content["linkedin_post"]

    image_prompt = content["image_prompt"]

    print("\nGenerated LinkedIn Post:\n")
    print(linkedin_post)

    print("\nGenerating image...\n")

    image_path = generate_image(image_prompt)

    if image_path:

        print("Posting to LinkedIn...\n")

        post_to_linkedin(
            linkedin_post,
            image_path
        )

        print("LinkedIn post published successfully.")

    else:

        print("Skipping LinkedIn post because image generation failed.")


if __name__ == "__main__":
    run_pipeline()
