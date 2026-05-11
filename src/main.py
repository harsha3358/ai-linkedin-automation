from scrape_news import fetch_ai_news
from rank_news import rank_articles

from generate_post import generate_content

from generate_image import generate_image

from post_linkedin import post_to_linkedin


def run_pipeline():

    print("Fetching latest AI news...")

    articles = fetch_ai_news()

    print("Ranking news...")

    best_article = rank_articles(articles)

    print("\nBest Article:\n")
    print(best_article)

    print("\nGenerating AI content...\n")

    content = generate_content(best_article)

    linkedin_post = content["linkedin_post"]

    image_prompt = content["image_prompt"]

    print("\nLINKEDIN POST:\n")
    print(linkedin_post)

    print("\nIMAGE PROMPT:\n")
    print(image_prompt)

    print("\nGenerating cinematic image...\n")

    image_path = generate_image(image_prompt)

    print(f"\nImage saved at: {image_path}")

    print("\nPosting to LinkedIn...\n")

    post_to_linkedin(linkedin_post)

    print("\nDONE 🚀")


if __name__ == "__main__":
    run_pipeline()