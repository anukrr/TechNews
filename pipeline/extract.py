"""This script extracts story information from the Hacker News API."""

import logging
import pandas as pd
from requests import get, exceptions
from dotenv import load_dotenv

BASE_URL = "https://hacker-news.firebaseio.com/v0/"
STORY_COUNT = 200


def get_top_stories(count: int) -> list:
    """Returns the ids of the top 200 stories on Hacker News."""
    if not isinstance(count, int):
        raise TypeError("Count must be an integer.")

    try:
        top_stories = get(BASE_URL + "topstories.json", timeout=100).json()
        return top_stories[:count]
    except (exceptions.RequestException, exceptions.HTTPError, ValueError) as error:
        logging.exception("An error occurred: %s", error)
        raise


def extract_story_info(story_id: int) -> dict:
    """Finds the details of a given story on Hacker News based on the story id."""
    try:
        story_info = get(BASE_URL + "item/" + str(story_id) +
                         ".json", timeout=100).json()
    except (exceptions.RequestException, exceptions.HTTPError, ValueError) as error:
        logging.exception("An error occurred: %s", error)
        raise

    relevant_cols = ["id", "title", "by", "url",
                     "time", "score", "descendants", "type"]
    story_dict = {col: story_info.get(col) for col in relevant_cols}
    return story_dict


def generate_dataframe(row_count: int) -> None:
    """Collects information on chosen number of top stories and returns them in a dataframe."""
    story_ids = get_top_stories(row_count)
    all_stories = [extract_story_info(id) for id in story_ids]
    return pd.DataFrame(all_stories)


if __name__ == "__main__":
    load_dotenv()
    generate_dataframe(200).to_csv('outputs/extract.csv', index=False)
