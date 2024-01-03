"""This script extracts story information from the Hacker News API."""
import pandas as pd
from requests import get


BASE_URL = "https://hacker-news.firebaseio.com/v0/"
STORY_COUNT = 200


def get_top_stories(count: int) -> list:
    """Returns the ids of the top 200 stories on Hacker News."""
    top_stories = get(BASE_URL + "topstories.json", timeout=100).json()
    return top_stories[:count]
    

def extract_story_info(story_id: int) -> dict:
    """Finds the details of a given story on Hacker News based on the story id."""
    story_info = get(BASE_URL + "item/" + str(story_id) +
                     ".json", timeout=100).json()
    relevant_cols = ["id", "title", "by", "url",
                     "time", "score", "descendants", "type"]
    story_dict = {col: story_info.get(col) for col in relevant_cols}
    return story_dict


def main() -> None:
    """Collects information on the 200 top stories and stores it in a csv file."""
    story_ids = get_top_stories(STORY_COUNT)

    all_stories = [extract_story_info(id) for id in story_ids]

    stories_df = pd.DataFrame(all_stories)
    stories_df.to_csv("all_stories.csv", index=False)


if __name__ == "__main__":

    main()
