"""Streamlit dashboard for analysis of stories"""
from os import environ
from psycopg2 import connect
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import altair as alt 
from sql_queries import LONGEST_LASTING_DF, COMMENTS


def get_db_connection():
    """Returns a database connection."""
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
    

def font_color_topics(val):
    color_mapping = {
        'Programming & Software Development': "red",
        'Game Development': "blue",
        'Algorithms & Data Structures': "green",
        'Web Development & Browser Technologies': "gray",
        'Computer Graphics & Image Processing': "orange",
        'Operating Systems & Low-level Programming': "black",
        'Science & Research Publications': "pink",
        'Literature & Book Reviews': "violet",
        'Artificial Intelligence & Machine Learning': "purple",
        'News & Current Affairs': "aqua",
        'Miscellaneous & Interesting Facts': "brown"
    }
    return f'color: {color_mapping.get(val, "black")}'


def show_long_lived_stories(connection):
    """Returns a reading table with top 5 longest"""

    df = pd.read_sql(LONGEST_LASTING_DF, connection)
    df = df.rename(columns={"title": "Title",
                            "name": "Topic",
                            "longest_stories": "Hours spent in Top Stories"}, errors="raise")
    
    st.write(f"Stories which have stayed in Top Stories the longest ")

    # Apply the font color function to the 'Topic' column
    styled_df = df.style.apply(lambda x: x.map(font_color_topics), subset=['Topic'])

    # Display the styled DataFrame in Streamlit
  
    return st.dataframe(styled_df)


def show_comments_line_chart(connection):
    """Returns a reading table with top 5 longest"""

    df = pd.read_sql(COMMENTS, connection)
    
    grouped_df = df.groupby(['story_id', 'record_time']).sum().reset_index()

    print(grouped_df)

    st.write(f"How comments change over time")
  
    return st.line_chart(grouped_df.set_index('record_time'))


if __name__ == "__main__":

    load_dotenv()
    conn = get_db_connection()

    with conn:
        reading_data = pd.read_sql('SELECT * FROM records WHERE ;', conn)

        show_long_lived_stories(conn)
        show_comments_line_chart(conn)
