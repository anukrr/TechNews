"""Streamlit dashboard for analysis of stories"""
from os import environ
from datetime import datetime, timedelta

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, URL
from streamlit_marquee import streamlit_marquee

from dashboard_functions import (generate_dataframe, top_stories_table, top_comments_table,
                                 topic_table, trending_stories_table, topic_piechart,
                                 format_trending_stories)

load_dotenv()

engine_url_object = URL.create("postgresql+psycopg2",
                               username=environ["DB_USER"],
                               password=environ["DB_PASSWORD"],
                               host=environ["DB_HOST"],
                               database=environ["DB_NAME"])

engine = create_engine(engine_url_object)


st. set_page_config(page_title="The Full Stack",
                    page_icon="🌐",
                    layout="wide")


with st.sidebar:
    st.subheader("🕒 Timeframe")
    timeframe = st.selectbox("Filter", ["hour","day","week"])
    all_data = generate_dataframe(engine, timeframe)

    st.divider()

    st.subheader("🔎 Topics")
    selected_topics = st.multiselect(
        "Filter", all_data["name"].dropna().unique(),
        default=all_data["name"].dropna().unique())


st.image("full-stack.png", width=500)

st.markdown("##### *Stay ahead of the curve with the latest tech news & trends*", unsafe_allow_html=False, help=None)

marquee_trending = trending = trending_stories_table(engine, "hour", selected_topics)
marquee = streamlit_marquee(**{
        # the marquee container background color
        'background': "#005864",
        # the marquee text size
        'font-size': '20px',
        # the marquee text color
        "color": "#ffffff",
        # the marquee text content
        'content': format_trending_stories(marquee_trending),
        # the marquee container width
        'width': '2000px',
        # the marquee container line height
        'lineHeight': "20px",
        # the marquee duration
        'animationDuration': '60s',
        })


top_scores = top_stories_table(all_data, selected_topics)

st.markdown("### ⚡ Top Stories", unsafe_allow_html=False, help="Stories are ranked based on their total score.")
st.markdown(f"##### In the past {timeframe}")
st.dataframe(top_scores.style,
                use_container_width=True,
                hide_index=True,
                height=175,
                column_config={"🔗": st.column_config.LinkColumn()})

st.markdown("### 📈 Trending Stories",
            unsafe_allow_html=False,
            help="Stories are ranked by their score increase over a given timeframe.")
if timeframe in ("hour","day"):
    trending = trending_stories_table(engine, timeframe, selected_topics)
    st.markdown(f"##### In the past {timeframe}")
    st.dataframe(trending,
                 use_container_width=True,
                 hide_index=True,
                 height=175,
                 column_config={"🔗": st.column_config.LinkColumn()})
else:
    st.markdown("##### can only be displayed by hour or day")

st.divider()

col1, col2 = st.columns([3,3])


with col1:

    topic_piechart = topic_piechart(all_data)
    st.markdown("### 🔥 Hot Topics",
                help="Proportion of scores given for each topic.")
    st.markdown(f"##### In the past {timeframe}")
    st.altair_chart(topic_piechart,
                    use_container_width=True)


with col2:

    top_comments = top_comments_table(all_data, selected_topics)
    st.markdown("### 💬 Causing a Discussion",
                help="Stories are ranked by their comment count.")
    st.markdown(f"##### In the past {timeframe}")
    st.dataframe(top_comments,
                 use_container_width=True,
                 hide_index=True,
                 height=300,
                 column_config={"🔗": st.column_config.LinkColumn()})
