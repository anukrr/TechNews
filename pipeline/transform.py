"""This script cleans the data collected from the Hacker News API."""
import pandas as pd
from datetime import datetime


def clean_dataframe(stories_df: pd.DataFrame) -> pd.DataFrame:
    """Formats the dataframe correctly and removes invalid entries."""
    stories_df["time"] = pd.to_datetime(stories_df["time"], unit="s")
    stories_df['descendants'] = stories_df['descendants'].fillna(0).astype(int)
    stories_df = stories_df.rename(columns={"descendants": "comments",
                                            "by": "author",
                                            "time": "creation_date",
                                            "url": "story_url"})
    stories_df = stories_df[stories_df.type == "story"]
    stories_df = stories_df.drop(columns="type")

    return stories_df


if __name__ == "__main__":

    story_df = pd.read_csv("all_stories.csv", index_col=False)
    clean_stories = clean_dataframe(story_df)
    clean_stories.to_csv("clean_all_stories.csv", index=False)
