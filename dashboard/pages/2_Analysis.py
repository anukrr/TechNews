"""Full comment analysis. Works by importing from helper files."""
from os import environ

import streamlit as st
from dotenv import load_dotenv
import psycopg2

from helper_comments_gauge import make_gauge_chart
from helper_comments_expander import make_expander

def get_db_connection():
    """Returns a database connection."""
    load_dotenv()
    return psycopg2.connect(
        host=environ["DB_HOST"],
        port=environ["DB_PORT"],
        database=environ["DB_NAME"],
        user=environ["DB_USER"],
        password=environ["DB_PASSWORD"]
        )


def get_story_id_from_url(story_url: str) -> int:
    """Gets the story_id from a story_url."""
    query = """
        SELECT story_id
        FROM stories
        WHERE stories.story_url LIKE %s;
        """
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(query, (f'%{story_url}%',))
        result = cur.fetchone()
        if result:
            return result[0]

if __name__ == "__main__":

    st.title('Analysis')
    st.subheader('URL NLP')
    st.markdown("##### Use our tool to find out what people really feel about a story! ",)

    st.divider()
    url = st.text_input('Enter a URL')
    if url:

        st.write('Article', url)
        INPUT_STORY_ID = get_story_id_from_url(url)

        st.write("Sentiment for this story:")
        make_gauge_chart(INPUT_STORY_ID)

        st.subheader('Most discussed comments')
        st.write("Check out the top talking points for this story:")
        make_expander(INPUT_STORY_ID)

    else:
        st.write("Waiting for a story...")
