"""Routine script that checks how much database entries change based on score."""
from os import environ
from dotenv import load_dotenv
import psycopg2
import pandas as pd


load_dotenv()

THRESHOLD = 20
STORY_LIMIT = 200


def get_db_connection():
    """Forms AWS RDS postgres connection."""
    try:
        conn = psycopg2.connect(dbname=environ["DB_NAME"],
            host=environ["DB_HOST"],
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"],
            port=environ["DB_PORT"])
        return conn
    except Exception as e:
        print('Error: Unable to form connection %s', e)


def viral_checker(threshold: int, story_limit: int) -> list[dict]:
    """Returns a list of dictionaries with each story above the score threshold."""

    viral_query = """
        WITH LatestTwoRecords AS (
        SELECT
            story_id,
            score,
            ROW_NUMBER() OVER (PARTITION BY story_id ORDER BY record_time DESC) AS row_num
        FROM
            records
        )
        SELECT
            story_id,
            COALESCE(MAX(CASE WHEN row_num = 1 THEN score END) - MAX(CASE WHEN row_num = 2 THEN score END), 0) AS score_difference
        FROM
            LatestTwoRecords
        WHERE
            row_num <= 2
            AND story_id IN (SELECT story_id FROM records ORDER BY record_id DESC LIMIT (%s))
        GROUP BY
            story_id
        HAVING
            COALESCE(MAX(CASE WHEN row_num = 1 THEN score END) - MAX(CASE WHEN row_num = 2 THEN score END), 0) > (%s)
        ORDER BY
            score_difference DESC;
        """

    conn = get_db_connection()
    with conn.cursor() as curr:
        curr.execute(viral_query, (story_limit, threshold))
        story_ids = tuple([story_id[0] for story_id in curr.fetchall()])
        story_info_query = f"""SELECT title, story_url FROM stories WHERE story_id IN {story_ids};"""
        curr.execute(story_info_query)
        story_info = curr.fetchall()
        story_info = pd.read_sql(story_info_query, conn)
    story_info = story_info.to_dict(orient="records")
    return story_info


if __name__ == "__main__":
    
    viral_checker(THRESHOLD, STORY_LIMIT)
