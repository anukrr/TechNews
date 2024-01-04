"""Routine script that checks how much database entries change based on score."""
from os import environ
from dotenv import load_dotenv
import psycopg2

load_dotenv()

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
        print(f'Error: Unable to form connection {e}')


def viral_checker(threshold: int):
    conn = get_db_connection()
    with conn.cursor() as curr:
        curr.execute(f"""
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
            AND story_id IN (SELECT story_id FROM records ORDER BY record_id DESC LIMIT 200)
        GROUP BY
            story_id
        HAVING
            COALESCE(MAX(CASE WHEN row_num = 1 THEN score END) - MAX(CASE WHEN row_num = 2 THEN score END), 0) > {threshold}
        ORDER BY
            score_difference DESC;
        """)
        data = curr.fetchall()

        curr.close()
    print(data)


if __name__ == "__main__":
    
    viral_checker(100)
