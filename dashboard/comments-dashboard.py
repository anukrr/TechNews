

import streamlit as st
from helper_comments_gauge import make_gauge_chart
from helper_comments_expander import make_expander


if __name__ == "__main__":

    input_story_id = 38865518
    st.write(f"[TEMP] current story_id: {input_story_id}")

    # need to error filter for URLs not found at hackernews
    st.subheader('URL NLP analysis', divider='rainbow')
    url = st.text_input('Enter a URL', 'url')
    st.write('Article', url)

    st.header('Comment analysis on this story')

    st.subheader('How people feel about this story.', divider='rainbow')
    st.write("Sentiment for this story:")
    make_gauge_chart(input_story_id)

    st.subheader('Most discussed comments', divider='rainbow')
    st.write("Check out the top talking points for this story:")
    make_expander(input_story_id)
