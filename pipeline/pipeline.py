"""Runs the entire pipeline."""

from os import environ
from dotenv import load_dotenv
from openai import OpenAI
from extract import generate_dataframe
from transform import clean_dataframe
from load import get_db_connection, upload_latest_data



STORY_COUNT = 200



def run_pipeline(db_connection, client):
    """Contains the entire ETL pipeline flow."""

    # --- Extract---
    df = generate_dataframe(STORY_COUNT)
    print("Data extracted successfully.")

    # --- Transform ---
    cleaned_df = clean_dataframe(df, client)
    print("Data transformed successfully.")

    # --- Load ---
    upload_latest_data(cleaned_df, db_connection)
    print("Data uploaded successfully.")


if __name__=="__main__":
    load_dotenv()
    CLIENT = OpenAI(
        api_key = environ["OPENAI_API_KEY"]
    )

    connection = get_db_connection()
    run_pipeline(connection, CLIENT)
