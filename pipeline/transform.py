"""This script cleans & builds upon the data collected from the Hacker News API."""
from os import environ
from dotenv import load_dotenv
import pandas as pd

from openai import OpenAI
from pandarallel import pandarallel

load_dotenv()
VALID_TOPIC_IDS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11")
client = OpenAI(
    api_key=environ["OPENAI_API_KEY"]
)

pandarallel.initialize(progress_bar=True)


def generate_topic(story_url: str) -> str:
    """Finds the most suitable topic for a url from a predefined list of topics with the OpenAI API."""
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": """You are a classifying bot that can categorise urls into only these categories by returning the corresponding number:
         1. Programming & Software Development
         2. Game Development
         3. Algorithms & Data Structures
         4. Web Development & Browser Technologies
         5. Computer Graphics & Image Processing
         6. Operating Systems & Low-level Programming
         7. Science & Research Publications
         8. Literature & Book Reviews
         9. Artificial Intelligence & Machine Learning
         10. News & Current Affairs.
         11. Miscellaneous & Interesting Facts"""},
            {"role": "user",
             "content": f"""Categorise this url into one of the listed categories: {story_url}.
         Only state the category number and nothing else. Ensure your only output is a number."""}])
    return completion.choices[0].message.content


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
    stories_df["topic_id"] = stories_df["story_url"].parallel_apply(
        generate_topic)
    stories_df.loc[~stories_df["topic_id"].isin(
        VALID_TOPIC_IDS), "topic_id"] = None
    return stories_df


if __name__ == "__main__":

    story_df = pd.read_csv("extracted_stories.csv", index_col=False)
    clean_stories = clean_dataframe(story_df)
    clean_stories.to_csv("transformed_stories.csv", index=False)
