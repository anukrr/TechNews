"""Full comment analysis. Works by importing from helper files."""

import streamlit as st
from helper_comments_gauge import make_gauge_chart
from helper_comments_expander import make_expander


if __name__ == "__main__":

    INPUT_STORY_ID = 38865518
    st.write(f"[TEMP] current story_id: {INPUT_STORY_ID}")

    # need to error filter for URLs not found at hackernews
    st.subheader('URL NLP analysis', divider='rainbow')
    url = st.text_input('Enter a URL', 'url')
    st.write('Article', url)

    st.header('Comment analysis on this story')

    st.subheader('How people feel about this story.', divider='rainbow')
    st.write("Sentiment for this story:")
    make_gauge_chart(INPUT_STORY_ID)

    st.subheader('Most discussed comments', divider='rainbow')
    st.write("Check out the top talking points for this story:")
    make_expander(INPUT_STORY_ID)
