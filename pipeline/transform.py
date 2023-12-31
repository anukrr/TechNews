"""This script cleans & builds upon the data collected from the Hacker News API."""
from os import environ
import psycopg2
import logging
from dotenv import load_dotenv
import pandas as pd
import openai
from pandarallel import pandarallel

load_dotenv()
VALID_TOPIC_IDS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11")
client = openai.OpenAI(
    api_key=environ["OPENAI_API_KEY"]
)

pandarallel.initialize(progress_bar=True)


def get_db_connection():
    """Returns a database connection."""
    try:
        connection = psycopg2.connect(
            host=environ["DB_HOST"],
            port=environ["DB_PORT"],
            database=environ["DB_NAME"],
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"]
        )
        return connection
    except psycopg2.OperationalError as error:
        # Log the specific error details for troubleshooting
        logging.exception("Error connecting to the database: %s", error)
        raise


def handle_openai_errors(err):
    """OpenAI API request error-handling as per official docs."""
    if isinstance(err, openai.APIError):
        logging.exception("OpenAI API returned an API Error: %s", err)
    elif isinstance(err, openai.APIConnectionError):
        logging.exception("Failed to connect to OpenAI API: %s", err)
    elif isinstance(err, openai.RateLimitError):
        logging.exception("OpenAI API request exceeded rate limit: %s", err)
    else:
        logging.exception("Unexpected error: %s", err)

    raise err


def generate_topic(story_url: str) -> str:
    """Finds the most suitable topic for a url from a predefined list of topics 
    using the OpenAI API."""

    conn = get_db_connection()
    topic_query = f"SELECT topic_id FROM stories WHERE story_url = '{story_url}';"
    with conn.cursor() as cur:
        cur.execute(topic_query)
        topic_check = cur.fetchall()

    if not topic_check:
        system_content_spec = """
            You are a classifying bot that can categorise urls into only these categories by returning the corresponding number:
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
                11. Miscellaneous & Interesting Facts"""
        user_content_spec = f"""
            Categorise this url into one of the listed categories: {story_url}.
            Only state the category number and nothing else. Ensure your only output is a number."""

        try:
            completion = client.chat.completions.create(
                model=environ["GPT-MODEL"],
                messages=[
                    {"role": "system",
                     "content": system_content_spec},
                    {"role": "user",
                     "content": user_content_spec}])
            return completion.choices[0].message.content
        except openai.APIError as error:
            return handle_openai_errors(error)

    return str(topic_check[0][0])


def clean_dataframe(stories_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and formats the dataframe then inserts topics."""
    # Formats and cleans values
    stories_df["time"] = pd.to_datetime(stories_df["time"], unit="s")
    stories_df['descendants'] = stories_df['descendants'].fillna(0).astype(int)
    # Formats columns
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

    stories = pd.read_csv('outputs/extract.csv', index_col=False)
    stories = clean_dataframe(stories)
    stories.to_csv('outputs/cleaned.csv', index=False)
