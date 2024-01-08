"""Streamlit dashboard for analysis of stories"""
from os import environ
from datetime import datetime, timedelta

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, URL

now = datetime.now()
one_hour_ago = now - timedelta(hours=1)
one_day_ago = now - timedelta(days=1)

load_dotenv()

engine_url_object = URL.create(
        "postgresql+psycopg2",
        username=environ['DB_USER'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_HOST'],
        database=environ['DB_NAME'],
        )

engine = create_engine(engine_url_object)

topics = pd.read_sql("SELECT * FROM topics;", engine)

st. set_page_config(page_title="Tech News Summariser",
                    page_icon="🌐",
                    layout="wide")

with st.sidebar:
    st.header("Topics")
    selected_topics = st.multiselect(
        "Filter", topics["name"].unique(),default=topics["name"].unique())
    if len(selected_topics) > 1:
        topic_statement = f"AND topics.name in {tuple(selected_topics)}"
    elif len(selected_topics) == 1:
        topic_statement = f"AND topics.name = '{selected_topics[0]}'"
    else:
        topic_statement = ""

st.title("🌐 Tech News Summariser 🌐")

col1, col2, col3 = st.columns([3,0.5,2])

with col1:

    hourly_highest_score= pd.read_sql(f"""SELECT title, score, comments, story_url, topics.name
                        FROM records
                        LEFT JOIN stories
                        ON records.story_id = stories.story_id
                        INNER JOIN topics
                        ON stories.topic_id = topics.topic_id
                        WHERE record_time > '{one_hour_ago}' {topic_statement}
                        ORDER BY score DESC;""", engine, index_col="title")

    st.header("⚡ Top Stories")
    st.subheader("in the past hour")
    st.dataframe(hourly_highest_score.head(25))

    hourly_highest_comment = pd.read_sql(f"""SELECT title, score, comments, story_url, topics.name
                        FROM records
                        LEFT JOIN stories
                        ON records.story_id = stories.story_id
                        INNER JOIN topics
                        ON stories.topic_id = topics.topic_id
                        WHERE record_time > '{one_hour_ago}' {topic_statement}
                        ORDER BY comments DESC;""", engine, index_col="title")

    st.header("💬 Causing a Discussion")
    st.dataframe(hourly_highest_comment.head(25))


with col3:

    hot_topics = pd.read_sql(f"""
                             SELECT COUNT(*), topics.name as topic FROM records
                             LEFT JOIN stories
                             ON records.story_id = stories.story_id
                             INNER JOIN topics
                             ON stories.topic_id = topics.topic_id
                             WHERE record_time > '{one_day_ago}'
                             GROUP BY topics.name
                             ORDER BY COUNT(*) DESC;""", engine, index_col="topic")
    st.subheader("🔥 Whats Hot")
    st.dataframe(hot_topics.head(3))
    st.subheader("❌ Whats Not")
    st.dataframe(hot_topics.tail(3).sort_values(by="count", ascending=True))
