"""Streamlit dashboard for analysis of stories"""
from os import environ

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, URL, exc
from streamlit_marquee import streamlit_marquee

from dashboard_functions import (generate_dataframe, top_stories_table, top_comments_table,
                                  trending_stories_table, topic_piechart,
                                 format_trending_stories)

load_dotenv()

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


def create_marquee(connection, topics: list[str]):
    """Creates a marquee going across homepage."""

    marquee_trending  = trending_stories_table(connection, "hour", topics)
    streamlit_marquee(**{
        'background': "#005864",
        'font-size': '20px',
        "color": "#ffffff",
        'content': format_trending_stories(marquee_trending),
        'width': '2000px',
        'lineHeight': "20px",
        'animationDuration': '60s',
        })


def show_top_stories(data: pd.DataFrame, topics: list, timeframe):
    """Creates data table showing top stories within database."""

    top_scores = top_stories_table(data, topics)

    st.markdown("### ⚡ Top Stories", unsafe_allow_html=False,
                help="Stories are ranked based on their total score.")
    st.markdown(f"##### In the past {timeframe}")
    st.dataframe(top_scores.style,
                    use_container_width=True,
                    hide_index=True,
                    height=175,
                    column_config={"🔗": st.column_config.LinkColumn()})


def show_trending_stories(connection, chosen_timeframe, topics):
    """Creates data table showing trending stories within database."""

    st.markdown("### 📈 Trending Stories",
            unsafe_allow_html=False,
                help="Stories are ranked by their score increase over a given timeframe.")
    if chosen_timeframe in ("hour","day"):
        trending = trending_stories_table(connection, chosen_timeframe, topics)
        st.markdown(f"##### In the past {chosen_timeframe}")
        st.dataframe(trending,
                    use_container_width=True,
                    hide_index=True,
                    height=175,
                    column_config={"🔗": st.column_config.LinkColumn()})
    else:
        st.markdown("##### can only be displayed by hour or day")


if __name__ == "__main__":

    conn = get_db_connection()

    st. set_page_config(page_title="The Full Stack",
                        page_icon="🌐",
                        layout="wide")

    with st.sidebar:
        st.subheader("🕒 Timeframe")
        timeframe = st.selectbox("Filter", ["hour","day","week"])
        all_data = generate_dataframe(conn, timeframe)

        st.divider()

        st.subheader("🔎 Topics")
        selected_topics = st.multiselect(
            "Filter", all_data["name"].dropna().unique(),
            default=all_data["name"].dropna().unique())


    create_marquee(conn, selected_topics)

    st.image("full-stack.png", width=500)
    st.markdown("##### *Stay ahead of the curve with the latest tech news & trends*",
                unsafe_allow_html=False, help=None)
    st.title('Homepage')

    show_top_stories(all_data, selected_topics, timeframe)

    show_trending_stories(conn, timeframe, selected_topics)

    st.divider()

    col1, col2 = st.columns([3,3])

    with col1:

        topic_piechart(all_data, timeframe)

    with col2:

        top_comments_table(all_data, selected_topics, timeframe)
