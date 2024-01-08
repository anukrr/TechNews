"""Streamlit dashboard for analysis of stories"""
from os import environ
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from sqlalchemy import create_engine, URL
import matplotlib.pyplot as plt
import seaborn as sns
from sql_queries import (
LONGEST_LASTING_DF,
COMMENTS,
MOST_AUTHOR_CONTRIBUTIONS,
MOST_POPULAR_AUTHORS, 
LAST_HOUR_AVERAGE_SCORE,
LAST_HOUR_MEDIAN_SCORE
)


def get_db_connection():
    """Returns a database connection."""
    try:
        connection = URL.create(
        "postgresql+psycopg2",
        username=environ['DB_USER'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_HOST'],
        database=environ['DB_NAME'],
        )
        return create_engine(connection)
    except OSError:
        return {'error': 'Unable to connect to the database.'}
    


def font_color_topics(val) -> str:
    """Maps each possible story Topic to a colour"""

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

    st.write("Stories which have stayed in Top Stories the longest")

    # Apply the font color function to the 'Topic' column
    styled_df = df.style.apply(lambda x: x.map(font_color_topics), subset=['Topic'])

    # Display the styled DataFrame in Streamlit

    return st.dataframe(styled_df)


def show_comments_line_chart(connection):
    """Returns a reading table with top 5 longest"""

    df = pd.read_sql(COMMENTS, connection)

    grouped_df = df.groupby(['story_id', 'record_time']).sum().reset_index()

    st.write("How comments change over time")

    return st.line_chart(grouped_df.set_index('record_time'))


def show_recent_average_and_median(connection):
    """Returns a reading table with top 5 longest"""

    average_df = pd.read_sql(LAST_HOUR_AVERAGE_SCORE, connection)
    median_df = pd.read_sql(LAST_HOUR_MEDIAN_SCORE, connection)
    return average_df["avg"].round().iloc[0], median_df["median_score"].iloc[0]

    # grouped_df = df.groupby(['story_id', 'record_time']).sum().reset_index()

    # st.write("How comments change over time")

    # return st.line_chart(grouped_df.set_index('record_time'))


def show_top_authors(connection):
    
    df1 = pd.read_sql(MOST_AUTHOR_CONTRIBUTIONS, connection)
    df2 = pd.read_sql(MOST_POPULAR_AUTHORS, connection)
    # Display the results in Streamlit
    st.title("Top Authors Overview")

    # Display the results of the first SQL query
    # st.header("Authors with Most Contributions")
    # st.table(df1)

    # # Display the results of the second SQL query
    # st.header("Authors with Highest Scores")
    # st.table(df2)

    # Plot bar charts for better visualization
    fig, ax = plt.subplots(2, 1, figsize=(10, 12))

    # Bar chart for stories created
    ax[0].bar(df1['author'], df1['stories_created'], color='skyblue')
    ax[0].set_title('Top Authors by Stories Created')
    ax[0].set_ylabel('Number of Stories Created')
    ax[0].set_xlabel('Authors')
    ax[0].grid(axis='y', linestyle='--', alpha=0.7)

    # Bar chart for total votes
    ax[1].bar(df2['author'], df2['all_stories_total_votes'], color='lightcoral')
    ax[1].set_title('Top Authors by Total Votes')
    ax[1].set_ylabel('Total Votes')
    ax[1].set_xlabel('Authors')
    ax[1].grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Display the plots in Streamlit
    st.pyplot(fig)

if __name__ == "__main__":

    load_dotenv()
    conn = get_db_connection()

    reading_data = pd.read_sql('SELECT * FROM records;', conn)

    show_long_lived_stories(conn)
    avg, med = show_recent_average_and_median(conn)
    st.subheader(f"In the past hour the average votes of a story are: {avg}, whilst the median is {med}")

    show_top_authors(conn)
    show_recent_average_and_median(conn)

