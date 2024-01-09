"""Streamlit dashboard for analysis of stories"""
from os import environ
from datetime import datetime, timedelta

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, URL

from dashboard_functions import (generate_dataframe, top_stories_table, top_comments_table,
                                 topic_table, trending_stories_table, topic_piechart)

load_dotenv()

engine_url_object = URL.create("postgresql+psycopg2",
                               username=environ["DB_USER"],
                               password=environ["DB_PASSWORD"],
                               host=environ["DB_HOST"],
                               database=environ["DB_NAME"])

engine = create_engine(engine_url_object)


st. set_page_config(page_title="Tech News Summariser",
                    page_icon="🌐",
                    layout="wide")


with st.sidebar:
    st.header("🕒 Timeframe")
    timeframe = st.selectbox("Filter", ["hour","day","week"])

    all_data = generate_dataframe(engine, timeframe)
    st.divider()
    st.header("🔎 Topics")
    selected_topics = st.multiselect(
        "Filter", all_data["name"].dropna().unique(),
        default=all_data["name"].dropna().unique())


st.title("🌐 Tech News Summariser 🌐")


col1, col2, col3 = st.columns([3,0.5,2.25])

with col1:

    top_scores = top_stories_table(all_data, selected_topics)

    st.header("⚡ Top Stories")
    st.subheader(f"in the past {timeframe}")
    st.dataframe(top_scores.style,
                 hide_index=True,
                 height=300,
                 column_config={"Link": st.column_config.LinkColumn()})
    st.divider()
    st.header("📈 Trending Stories")
    if timeframe in ("hour","day"):
        trending = trending_stories_table(engine, timeframe, selected_topics)
        st.subheader(f"in the past {timeframe}")
        st.dataframe(trending, hide_index=True, height=300)
    else:
        st.subheader(f"can only be displayed by hour or day")


with col3:

    topic_piechart = topic_piechart(all_data)
    st.header("🔥 Hot Topics")
    st.subheader(f"in the past {timeframe}")
    st.altair_chart(topic_piechart, use_container_width=True)
    # ranked_topics = topic_table(all_data)
    # st.subheader("🔥 Whats Hot")
    # st.dataframe(ranked_topics.head(3), use_container_width=True)
    # st.subheader("❌ Whats Not")
    # st.dataframe(ranked_topics.tail(3).sort_values(by="score", ascending=True), use_container_width=True)
    st.divider()
    top_comments = top_comments_table(all_data, selected_topics)
    st.header("💬 Causing a Discussion")
    st.subheader(f"in the past {timeframe}")
    st.dataframe(top_comments,
                 hide_index=True,
                 height=300,
                 column_config={"Link": st.column_config.LinkColumn()})
