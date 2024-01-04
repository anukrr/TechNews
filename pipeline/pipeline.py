from extract import get_top_stories, extract_story_info, main
from transform import generate_topic, clean_dataframe
from load import get_db_connection, upload_latest_data





def run_pipeline():
    """Contains the entire ETL pipeline flow."""
    # --- Extract---
    get_top_stories
    extract_story_info
    main

    # --- Transform ---
    generate_topic
    clean_dataframe

    # --- Load ---
    

if __name__=="__main__":
    run_pipeline()