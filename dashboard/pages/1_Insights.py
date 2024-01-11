"""Streamlit dashboard for analysis of stories"""
from os import environ
import re
import time
import pandas as pd
from dotenv import load_dotenv
import altair as alt
import streamlit as st
from sqlalchemy import create_engine, URL, exc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sql_queries import (
LONGEST_LASTING_DF,
COMMENTS,
MOST_AUTHOR_CONTRIBUTIONS,
MOST_POPULAR_AUTHORS,
LAST_HOUR_AVERAGE_SCORE,
LAST_HOUR_MEDIAN_SCORE,
FIVE_BIGGEST_MOVERS,
NEW_ENTRIES
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
    except OSError as e:
        return {'error': f'{e},Unable to connect to the database.'}

    except exc.SQLAlchemyError as e: 
        return {'error': f'{e}, unable to connect to the database'}


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


def show_recent_average_and_median(connection):
    """Returns a reading table with top 5 longest"""
    pass


def show_flashpoints(connection):
    """Shows snap info of stories, median, average and new entries"""

    title_alignment="""<div style="text-align: center; font-size: 50px" > Quick Insights </div>"""
    st.markdown(title_alignment, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        timeframe = st.selectbox("Filter", ["1 Hour","6 Hours","24 Hours"])
        average_df = pd.read_sql(LAST_HOUR_AVERAGE_SCORE.format(f"'{timeframe}'"), connection)
        median_df = pd.read_sql(LAST_HOUR_MEDIAN_SCORE.format(f"'{timeframe}'"), connection)
        new_entries_df = pd.read_sql(NEW_ENTRIES.format(f"'{timeframe}'"), connection)
        avg = average_df["avg"].astype(int).iloc[0]
        med = median_df["median_score"].astype(int).iloc[0]
        new_movers = new_entries_df["unique_story_count"].iloc[0]

    col2.metric("Average Story Votes", avg, "1.2 °F")
    col3.metric("Median Story Votes", med, "-8%")
    col4.metric("Brand New Stories", new_movers, "-8%")
    
  


def show_long_lived_stories(connection):
    """Returns a reading table with top 5 longest"""
    title_alignment="""<div style="text-align: center; font-size: 50px" > Remained in Top Stories the longest </div>"""
    st.markdown(title_alignment, unsafe_allow_html=True)

    df = pd.read_sql(LONGEST_LASTING_DF, connection)
    df = df.rename(columns={"title": "Title",
                            "name": "Topic",
                            "longest_stories": "Hours spent in Top Stories"}, errors="raise")


    # Apply the font color function to the 'Topic' column
    styled_df = df.style.apply(lambda x: x.map(font_color_topics), subset=['Topic'])

    # Display the styled DataFrame in Streamlit

    return st.dataframe(styled_df, hide_index = True)


def show_comments_line_chart(connection):
    """Returns a reading table with top 5 longest"""

    df = pd.read_sql(COMMENTS, connection)

    grouped_df = df.groupby(['story_id', 'record_time']).sum().reset_index()

    st.write("How comments change over time")

    return st.line_chart(grouped_df.set_index('record_time'))



def show_top_authors(connection):
    """Produces bar chart of the top authors in terms of contributions
    and score of stories
    """

    df1 = pd.read_sql(MOST_AUTHOR_CONTRIBUTIONS, connection)
    df2 = pd.read_sql(MOST_POPULAR_AUTHORS, connection)

    fig, ax = plt.subplots(2, 1, figsize=(10, 12))

    ax[0].bar(df1['author'], df1['stories_created'], color='skyblue')
    ax[0].set_title('Top Authors by Stories Created')
    ax[0].set_ylabel('Number of Stories Created')
    ax[0].set_xlabel('Authors')
    ax[0].grid(axis='y', linestyle='--', alpha=0.7)

    ax[1].bar(df2['author'], df2['all_stories_total_votes'], color='lightcoral')
    ax[1].set_title('Top Authors by Total Votes')
    ax[1].set_ylabel('Total Votes')
    ax[1].set_xlabel('Authors')
    ax[1].grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()

    st.pyplot(fig)


def extract_publisher(url):
    """Extracts the publisher from a given story url
    """
    pattern = re.compile(r"https?://(?:www\.)?(.*?)\/(.*)")

    match = pattern.search(url)

    if match:
        result = match.group(1)
        if result.count(".") == 2:
            result = result.split(".")
            return result[1]
        return result.split(".")[0]

    return "No match found."


def show_top_publishers(connection):
    """Produces bar chart of the top authors in terms of contributions
    and score of stories
    """
    story_data = pd.read_sql('SELECT * FROM stories;', connection)

    story_publishers = story_data["story_url"].dropna().apply(extract_publisher)
    count_publishers_df = story_publishers.value_counts().head(5).reset_index(name="count")
    count_publishers_df = count_publishers_df.rename(
        columns={'story_url': 'Publisher', 'count': 'Stories published'}
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(
        count_publishers_df['Publisher'],
        count_publishers_df['Stories published'],
        color='green'
    )

    ax.set_xlabel('Publisher')
    ax.set_ylabel('Stories published')
    ax.set_title('Top Publishers by Counts')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Rotate x-axis labels for better readability
    ax.set_xticklabels(count_publishers_df['Publisher'], rotation=45, ha='right')

    st.pyplot(fig)


def show_five_biggest_movers(connection):
    """Produces line chart of 5 biggest movers in the last 24 hours
    """

    df_records = pd.read_sql(FIVE_BIGGEST_MOVERS, connection)
    df_records['record_time'] = pd.to_datetime(df_records['record_time'])

    fig, ax = plt.subplots(figsize=(10, 6))

    for title in df_records['title'].unique():
        data_for_story = df_records[df_records['title'] == title]
        ax.plot(data_for_story['record_time'], data_for_story['score'], label=f'{title}')

    # Set labels and title
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Votes')
    ax.set_title('')
    ax.legend()

    ax.set_xticklabels(df_records['record_time'], rotation=45, ha='right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))

    title_alignment="""<div style="text-align: center; font-size: 50px" >
                    5 biggest movers
                    </div>"""
    st.markdown(title_alignment, unsafe_allow_html=True)
    st.pyplot(fig)


if __name__ == "__main__":

    load_dotenv()
    conn = get_db_connection()

    reading_data = pd.read_sql('SELECT * FROM records;', conn)

    show_flashpoints(conn)

    with st.container():
        title_alignment="""<div style="text-align: center; font-size: 50px" > Distributor Information </div>"""
        st.markdown(title_alignment, unsafe_allow_html=True)
        cols = st.columns(2)
        with cols[0]:
            show_top_authors(conn)

        with cols[1]:
            show_top_publishers(conn)

    show_long_lived_stories(conn)
    show_five_biggest_movers(conn)

    query = """
    SELECT
        EXTRACT(HOUR FROM record_time) AS hour_of_day,
        SUM(score) AS total_votes
    FROM
        records
    GROUP BY
        hour_of_day
    ORDER BY
        total_votes DESC;
"""

    # Execute the query and get the results into a DataFrame
    df = pd.read_sql_query(query, conn)
    df = df.sort_values(by='total_votes', ascending=False)

    # Streamlit app
    st.title("Total Votes by Hour of the Day")

    # Create a bar chart using Matplotlib
    # fig, ax = plt.subplots()
    # ax.bar(df['hour_of_day'], (df['total_votes']), color='skyblue', width=0.6)
    # # ax.set_xticks(df['hour_of_day'])
    # # ax.set_xticklabels(df['hour_of_day'], rotation=90, ha='right')

    # ax.set_xlabel('Hour of the Day')
    # ax.set_ylabel('Total Votes')
    # ax.set_title('Total Votes by Hour of the Day')
    # ax.set_yticks([])
    # # Display the plot in Streamlit
    # st.pyplot(fig)

    chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('hour_of_day:O', title='Hour of the Day'),
    y=alt.Y('total_votes:Q', title='Total Votes', axis=None),
    color=alt.Color('hour_of_day:N', title='Hour of the Day'),
        tooltip=['hour_of_day:N', 'total_votes:Q']
    ).interactive()


    # Display the Altair chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
