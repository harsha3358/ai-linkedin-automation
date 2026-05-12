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

    print("Best Article:")
    print(best_article)

    print("Generating AI content...")

    content = generate_content(best_article)

    linkedin_post = content["linkedin_post"]
    image_prompt = content["image_prompt"]

    print("Trend Score:", content.get("trend_score"))

    print("Carousel Ideas:")
    print(content.get("carousel_ideas"))

    print("Meme Idea:")
    print(content.get("meme_idea"))

    print(linkedin_post)

    print("Generating image...")

    image_path = generate_image(image_prompt)

    print("Posting to LinkedIn...")

    post_to_linkedin(linkedin_post, image_path)

    print("DONE")


if __name__ == "__main__":
    run_pipeline()