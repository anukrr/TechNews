"""Runs the entire pipeline."""

import logging
from dotenv import load_dotenv

from extract import generate_dataframe
from transform import clean_dataframe
from load import get_db_connection, upload_latest_data


load_dotenv()
STORY_COUNT = 200


def run_pipeline():
    """Contains the entire ETL pipeline flow."""
    conn = get_db_connection()

    # --- Extract---
    df = generate_dataframe(STORY_COUNT)
    logging.info("Data extracted successfully.")

    # --- Transform ---
    cleaned_df = clean_dataframe(df)
    logging.info("Data transformed successfully.")

    # --- Load ---
    upload_latest_data(cleaned_df, conn)
    logging.info("Data uploaded successfully.")


if __name__ == "__main__":
    run_pipeline()
