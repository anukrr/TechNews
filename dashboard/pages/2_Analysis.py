"""Full comment analysis. Works by importing from helper files."""
from os import environ
import streamlit as st
from sqlalchemy import create_engine, URL, exc
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


def get_story_id_from_url(url: str) -> int:
    """Gets the story_id from a url."""
    query = """
        SELECT story_id
        FROM stories
        WHERE stories.story_url LIKE %s;
        """
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(query, (f'%{url}%',))
        result = cur.fetchone()
        if result:
            return result[0]

if __name__ == "__main__":

    # need to error filter for URLs not found at hackernews
    st.subheader('URL NLP analysis', divider='rainbow')
    st.subheader('Find out what people are saying!', divider='rainbow')
    url = st.text_input('Enter a URL')
    if url:
    
        st.write('Article', url)
        INPUT_STORY_ID = get_story_id_from_url(url)

        st.header('Comment analysis on this story')

        st.subheader('How people feel about this story.', divider='rainbow')
        st.write("Sentiment for this story:")
        make_gauge_chart(INPUT_STORY_ID)
        print("Gauged")

        st.subheader('Most discussed comments', divider='rainbow')
        st.write("Check out the top talking points for this story:")
        make_expander(INPUT_STORY_ID)
        print("Expanded")

