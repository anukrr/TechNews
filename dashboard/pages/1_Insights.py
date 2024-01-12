"""Streamlit dashboard for analysis of stories"""
from os import environ
import re
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
RECENT_AVERAGE_SCORE,
RECENT_MEDIAN_SCORE,
PREVIOUS_AVERAGE_SCORE,
PREVIOUS_MEDIAN_SCORE,
RECENT_NEW_ENTRIES,
PREVIOUS_NEW_ENTRIES,
FIVE_BIGGEST_MOVERS,
VOTES_BY_HOUR
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


def show_flashpoints(connection):
    """Shows snap info of stories, median, average and new entries"""

    st.markdown("### Quick Insights",)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        timeframe = st.selectbox("Filter", ["1 Hour","6 Hours","24 Hours"])

        average_df = pd.read_sql(
            RECENT_AVERAGE_SCORE.format(f"'{timeframe}'"), connection)
        prev_average_df = pd.read_sql(
            PREVIOUS_AVERAGE_SCORE.format(f"'{timeframe}'", f"'{timeframe}'"), connection)
        avg = int(average_df["avg"].iloc[0])
        prev_avg = int(prev_average_df["avg"].iloc[0])

        median_df = pd.read_sql(RECENT_MEDIAN_SCORE.format(f"'{timeframe}'"), connection)
        prev_median_df = pd.read_sql(
            PREVIOUS_MEDIAN_SCORE.format(f"'{timeframe}'", f"'{timeframe}'"), connection)
        med = int(median_df["median_score"].iloc[0])
        prev_med = int(prev_median_df["median_score"].iloc[0])

        new_entries_df = pd.read_sql(
            RECENT_NEW_ENTRIES.format(f"'{timeframe}'"), connection)
        prev_entries_df = pd.read_sql(
            PREVIOUS_NEW_ENTRIES.format(f"'{timeframe}'", f"'{timeframe}'"), connection)
        new_movers = int(new_entries_df["unique_story_count"].iloc[0])
        prev_movers = int(prev_entries_df["unique_story_count"].iloc[0])

    col2.metric("Average Story Votes", avg, avg - prev_avg)
    col3.metric("Median Story Votes", med, med - prev_med)
    col4.metric("Brand New Entries", new_movers, new_movers - prev_movers)


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

    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Votes')
    ax.set_title('')
    ax.legend()

    ax.set_xticklabels(df_records['record_time'], rotation=45, ha='right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))

    st.markdown("#### Top 5 Biggest Movers Last 24 Hours",)

    st.pyplot(fig)


def show_long_lived_stories(connection):
    """Returns a reading table with stories which have stayed in top 5 for the longest longest"""

    st.markdown("#### Longest-Lived In Top Stories",)

    df = pd.read_sql(LONGEST_LASTING_DF, connection)
    df = df.rename(columns={"title": "Title",
                            "name": "Topic",
                            "longest_stories": "Hours spent in Top Stories"}, errors="raise")

    return st.dataframe(df, hide_index = True)


def show_votes_by_hour(connection):
    """Returns an Altair chart showing all the votes of all
    stories per hour
    """
    st.markdown("### Total Votes Every Hour - All Stories",)

    df = pd.read_sql(VOTES_BY_HOUR, connection)

    chart = alt.Chart(df).mark_line().encode(
    x=alt.X('hour_of_day:O', title='Hour of the Day'),
    y=alt.Y('total_votes:Q', title='Total Votes'),
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":

    load_dotenv()
    conn = get_db_connection()

    reading_data = pd.read_sql('SELECT * FROM records;', conn)

    st.title('Insights')

    show_flashpoints(conn)

    with st.container():

        st.markdown("### Distributors",)

        cols = st.columns(2)
        with cols[0]:
            show_top_authors(conn)

        with cols[1]:
            show_top_publishers(conn)

    st.divider()


    with st.container():
        cols2 = st.columns(2, gap="medium")
        with cols2[0]:
            show_five_biggest_movers(conn)

        with cols2[1]:
            show_long_lived_stories(conn)

        st.divider()
        show_votes_by_hour(conn)
