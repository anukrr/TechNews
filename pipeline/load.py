"""Load script that insert data into RDS."""

from os import environ
import logging
import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv()


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


def upload_latest_data(df: pd.DataFrame, connection) -> None:
    """Gets stories and records data from dataframe. Uploads it to database tables.
    If story is already in story table then values are updated with latest version."""

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

    with connection.cursor() as cursor:
        stories_columns = df[["id", "title", "author",
                              "story_url", "creation_date", "topic_id"]]
        records_columns = df[["id", "score", "comments"]]

        stories_insert = stories_columns.values.tolist()
        records_insert = records_columns.values.tolist()

        # execute_values is a faster option if necessary, but you have to rework the query etc.
        cursor.executemany(
            story_query, stories_insert)
        cursor.executemany(
            record_query, records_insert)
        connection.commit()


if __name__ == "__main__":

    data = pd.read_csv('clean_all_stories.csv')
    conn = get_db_connection()
    upload_latest_data(data, conn)
