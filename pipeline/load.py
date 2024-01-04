"Loads script to insert data into RDS."

from os import environ
import pandas as pd
from psycopg2 import connect
from dotenv import load_dotenv


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


def upload_latest_data(df: pd.DataFrame) -> None:
    """Gets stories and records data from dataframe. Uploads it to database tables.
    If story is already in story table then values are updated with latest version.
    """

    story_query = """
            INSERT INTO stories
                (story_id, title, author, story_url, creation_date, topic_id)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (story_id)
            DO UPDATE SET (title, author, story_url, creation_date, topic_id) = (EXCLUDED.title, EXCLUDED.author, EXCLUDED.story_url, EXCLUDED.creation_date, EXCLUDED.topic_id)
            ;
            """

    record_query = """
            INSERT INTO records
                (story_id, score, comments)
            VALUES
                (%s, %s, %s)
            ;
            """

    conn = get_db_connection()

    with conn.cursor() as cursor:
        stories_columns = df[["id","title","author","story_url","creation_date", "topic_id"]]
        stories_insert = stories_columns.values.tolist()

        records_columns = df[["id", "score", "comments"]]
        records_insert = records_columns.values.tolist()
        
        # execute_values is a faster option if necessary, but you have to rework the query etc.
        cursor.executemany(
            story_query, stories_insert)
        cursor.executemany(
            record_query, records_insert)
        conn.commit()


if __name__ == "__main__":
    data = pd.read_csv('clean_all_stories.csv')
    upload_latest_data(data)
