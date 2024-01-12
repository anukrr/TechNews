"""This file contains the functions necessary to generate the Streamlit dashboard."""

import time
from os import environ
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import altair as alt
from sqlalchemy import create_engine, URL
from sqlalchemy.engine.base import Engine

load_dotenv()

engine_url_object = URL.create("postgresql+psycopg2",
                               username=environ["DB_USER"],
                               password=environ["DB_PASSWORD"],
                               host=environ["DB_HOST"],
                               database=environ["DB_NAME"])


def generate_dataframe(engine: Engine, timeframe: str) -> pd.DataFrame:
    """Returns a comprehensive dataframe containing information on
    stories, records and topics."""
    current_time = datetime.now()
    if timeframe not in ("hour","day", "week"):
        return None
    if timeframe == "hour":
        time_cutoff = current_time - timedelta(hours=1)
    if timeframe == "day":
        time_cutoff = current_time - timedelta(days=1)
    if timeframe == "week":
        time_cutoff = current_time - timedelta(days=7)

    query = f"""
    SELECT records.record_id, records.story_id, records.score, records.comments, stories.title, stories.story_url, topics.name
    FROM records
    LEFT JOIN stories
    ON records.story_id = stories.story_id
    LEFT JOIN topics
    ON stories.topic_id = topics.topic_id
    WHERE record_time > '{time_cutoff}';"""

    dataframe = pd.read_sql(query, engine, index_col="record_id")

    return dataframe


def top_stories_table(dataframe: pd.DataFrame, topics: list) -> pd.DataFrame:
    """Finds the stories with the highest score."""
    dataframe = dataframe[dataframe["name"].isin(topics)]
    idx = dataframe.groupby("story_id")["score"].idxmax()
    max_scores = dataframe.loc[idx]
    max_scores = max_scores[["title","score","comments","story_url","name"]]
    max_scores["story_url"] = max_scores["story_url"].fillna(value="https://news.ycombinator.com/")
    max_scores = max_scores.rename(columns={
        "title": "Title",
        "score": "⬆️",
        "comments": "💬",
        "story_url": "🔗",
        "name": "Topic"
    })
    max_scores = max_scores.sort_values("⬆️", ascending=False).head(20)
    return max_scores


def top_comments_table(dataframe: pd.DataFrame, topics: list, timeframe) -> pd.DataFrame:
    """Finds the stories with the highest comment count."""
    dataframe = dataframe[dataframe["name"].isin(topics)]
    idx = dataframe.groupby("story_id")["comments"].idxmax()
    max_comments = dataframe.loc[idx]
    max_comments = max_comments[["title","score","comments","story_url","name"]]
    max_comments["story_url"] = max_comments["story_url"].fillna(
        value="https://news.ycombinator.com/")
    max_comments = max_comments.rename(columns={
        "title": "Title",
        "score": "⬆️",
        "comments": "💬",
        "story_url": "🔗",
        "name": "Topic"
    })
    st.markdown("### 💬 Causing a Discussion",
                help="Stories are ranked by their comment count.")
    st.markdown(f"##### In the past {timeframe}")
    st.dataframe(max_comments,
                 use_container_width=True,
                 hide_index=True,
                 height=300,
                 column_config={"🔗": st.column_config.LinkColumn()})
    return max_comments.sort_values("💬", ascending=False).head(20)


def trending_stories_table(engine: Engine, timeframe: str, topics: list) -> pd.DataFrame:
    """Finds the stories with the largest score increase in a given timeframe."""
    if timeframe not in ("hour","day"):
        return None
    if timeframe == "hour":
        interval = "2 hours"
    if timeframe == "day":
        interval = "24 hours"

    trend_query = f"""
            SELECT
                records.story_id,
                MAX(score) - MIN(score) AS score_change,
                stories.title,
                stories.story_url,
                MAX(record_time) AS latest_update,
                topics.name AS topic
            FROM records
            JOIN stories ON records.story_id = stories.story_id
            JOIN topics ON stories.topic_id = topics.topic_id
            WHERE record_time >= NOW() - INTERVAL '{interval}'
            GROUP BY records.story_id, stories.title, stories.story_url, topics.name
            ORDER BY score_change DESC;
            """
    trending_df = pd.read_sql(trend_query, engine, index_col="story_id")
    trending_df = trending_df[trending_df["topic"].isin(topics)]
    trending_df["story_url"] = trending_df["story_url"].fillna(
        value="https://news.ycombinator.com/")
    trending_df = trending_df.rename(columns={
        "title": "Title",
        "score_change": "➕",
        "comments": "💬",
        "story_url": "🔗",
        "topic": "Topic"
    })
    return trending_df[["Title","➕","🔗","Topic"]].head(10)


def topic_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Ranks topics based on associated story scores."""
    rankings = dataframe.groupby("name").sum()
    return rankings[["score"]].sort_values("score", ascending=False)


def topic_piechart(dataframe: pd.DataFrame, timeframe):
    """Creates a piechart showing score distribution for topics."""
    rankings = dataframe.groupby("name").sum().reset_index()
    rankings = rankings[["name","score"]].sort_values("score", ascending=False)
    piechart = alt.Chart(rankings).mark_arc(innerRadius=40,outerRadius=110).encode(theta=alt.Theta("score").stack(True),
                                                               color=alt.Color("name:N", sort="descending").scale(scheme="tableau20").legend(title="Topics",
                                                                                                                          orient="right",
                                                                                                                          titleFontSize=0,
                                                                                                                          labelFontSize=10,
                                                                                                                          labelLimit=0,                                                                                           labelColor="black"))
    piechart = piechart.properties(width=250, height=350)
    st.markdown("### 🔥 Hot Topics",
                help="Proportion of scores given for each topic.")
    st.markdown(f"##### In the past {timeframe}")
    st.altair_chart(piechart,
                    use_container_width=True)

    return piechart


def cycle_text(text_list, interval=4):
    index = 0
    box = st.empty()
    while True:
        box.write(f'{text_list[index]}')  # st.text(text_list[index])
        time.sleep(interval)
        index = (index + 1) % len(text_list)


def format_trending_stories(dataframe: pd.DataFrame) -> list[str]:
    """Turns trending story titles into a formatted list for the text cycler."""
    titles = dataframe["Title"].to_list()
    formatted_string = ""
    for title in titles:
        formatted_string += f"\n{title}------------------------------"
        formatted_string += ""
    return formatted_string


if __name__ == "__main__":

    engine = create_engine(engine_url_object)

    # df = generate_dataframe(engine, "hour")
    topics = ['News & Current Affairs' 'Programming & Software Development',
    'Literature & Book Reviews', 'Science & Research Publications',
    'Miscellaneous & Interesting Facts',
    'Artificial Intelligence & Machine Learning', 'Game Development',
    'Algorithms & Data Structures',
    'Operating Systems & Low-level Programming',
    'Computer Graphics & Image Processing']

    print(trending_stories_table(engine, "hour", topics))
