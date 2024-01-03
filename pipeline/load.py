"Loads script to insert data into RDS."

from os import environ
import pandas as pd
from psycopg2 import connect
from psycopg2 import extras
from dotenv import load_dotenv
import pprint


def get_db_connection():
    """Returns a database connection."""
    load_dotenv()
    try:
        connection = connect(
            host=environ["DB_HOST"],
            port=environ["DB_PORT"],
            database=environ["DB_NAME"],
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"]
        )
        return connection
    except OSError:
        return {'error': 'Unable to connect to the database.'}


def split_df(df: pd.DataFrame) -> tuple:
    pass


def upload_stories(df: pd.DataFrame) -> None:
    """Uploads dataframe to stories table. If value already """
    # topic_id

    query = """
            INSERT INTO stories
                (story_id, title, author, topic_id, story_url, creation_date)
            VALUES 
                (%s, %s, %s, %s, %s)
            ON CONFLICT (story_id)
            DO UPDATE SET (title, author, story_url, creation_date) = (EXCLUDED.title, EXCLUDED.author, EXCLUDED.story_url, EXCLUDED.creation_date);
            """

    conn = get_db_connection()
    with conn.cursor() as cursor:

        stories = df.values.tolist()[:5]
        stories_insert = [story[:5] for story in stories]

        # execute_values is a faster option if necessary, but you have to rework the query etc.
        cursor.executemany(
            query, [story for story in stories_insert])

        conn.commit()

    pprint.pprint(stories_insert)


# upload to records
# def upload(dataframe: pd.DataFrame):
#     """Uplaods"""
#     conn = get_db_connection()
#     pass


if __name__ == "__main__":
    df = pd.read_csv('clean_all_stories.csv')
    upload_stories(df)
