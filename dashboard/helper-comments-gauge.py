"""Script containing helper functions for comment analysis sentiment gauge plot."""

import requests

BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"


def get_parent_comment_ids(story: int) -> list:
    """
    Returns the id of comments from given story on Hacker News.
    """
    story_info = requests.get(BASE_URL + f"{story}.json", timeout=30).json()
    comment_ids = story_info.get("kids")  # Warning: read
    return comment_ids
