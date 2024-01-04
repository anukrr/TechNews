"""This script extracts story information from the Hacker News API."""
import pandas as pd
from requests import get, exceptions

import logging


BASE_URL = "https://hacker-news.firebaseio.com/v0/"
STORY_COUNT = 200


def get_top_stories(count: int) -> list:
    """Returns the ids of the top 200 stories on Hacker News."""
    try:
        top_stories = get(BASE_URL + "topstories.json", timeout=100).json()
        return top_stories[:count]
    except exceptions.RequestException as e:
         print(f"Error getting api request {e}")
    

def extract_story_info(story_id: int) -> dict:
    """Finds the details of a given story on Hacker News based on the story id."""
    try:
        story_info = get(BASE_URL + "item/" + str(story_id) +
                        ".json", timeout=100).json()
        relevant_cols = ["id", "title", "by", "url",
                        "time", "score", "descendants", "type"]
        story_dict = {col: story_info.get(col) for col in relevant_cols}
        return story_dict
    except Exception as e:
         print(f"Error extracting story information {e}")


def main() -> None:
    """Collects information on the 200 top stories and stores it in a csv file."""
    try:
        logging.info("Extraction Started.")
        story_ids = get_top_stories(STORY_COUNT)

        all_stories = [extract_story_info(id) for id in story_ids]

        stories_df = pd.DataFrame(all_stories)
        stories_df.to_csv("all_stories.csv", index=False)
        logging.info("Extracted Complete.")
    except Exception as e:
        print(f"Error extracting stories from api: {e}")


if __name__ == "__main__":
        main()

