"""Routine script that checks how much database entries change based on score."""
from os import environ
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, URL

load_dotenv()

THRESHOLD = 100
STORY_LIMIT = 200

engine_url_object = URL.create(
        "postgresql+psycopg2",
        username=environ['DB_USER'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_HOST'],
        database=environ['DB_NAME'],
        )


def viral_checker(threshold: int, story_limit: int) -> list[dict]:
    """Returns a list of dictionaries with each story above the score threshold."""
    # look into being able to return a %growth
    viral_query = f"""
        WITH LatestTwoRecords AS (
        SELECT
            story_id,
            score,
            ROW_NUMBER() OVER (PARTITION BY story_id ORDER BY record_time DESC) AS row_num
        FROM
            records
        )
        SELECT
            story_id
        FROM
            LatestTwoRecords
        WHERE
            row_num <= 2
            AND story_id IN (SELECT story_id FROM records ORDER BY record_id DESC LIMIT {story_limit})
        GROUP BY
            story_id
        HAVING
            COALESCE(MAX(CASE WHEN row_num = 1 THEN score END) - MAX(CASE WHEN row_num = 2 THEN score END), 0) > {threshold};
        """
    engine = create_engine(engine_url_object)

    story_ids = tuple(pd.read_sql(viral_query, engine)["story_id"].to_list())
    story_info_query = f"""SELECT title, story_url FROM stories WHERE story_id IN {story_ids};"""
    story_info = pd.read_sql(story_info_query, engine).to_dict(orient="records")
    return story_info


if __name__ == "__main__":

    viral_checker(THRESHOLD, STORY_LIMIT)
