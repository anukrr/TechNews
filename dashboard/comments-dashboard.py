import re
import html
import streamlit as st
from requests import get
import pandas as pd
from helper_comments_gauge import make_gauge_chart
from helper_comments_expander import generate_comments_df, get_top_5_most_replied_parent_comments


if __name__ == "__main__":

    # need to error filter for URLs not found at hackernews
    st.subheader('URL NLP analysis', divider='rainbow')
    url = st.text_input('Enter a URL', 'url')
    st.write('Article', url)

    st.subheader('NLP gauge chart.', divider='rainbow')
    gauge_chart()

    st.subheader('URL NLP analysis', divider='rainbow')
    st.write("Chec out the top talking points for this story:")

    story_id = 38865518
    top_5_comments = get_top_5_most_replied_parent_comments(story_id)

    # text_list = get_string_list()
    # cycle_text(text_list)

    df = generate_comments_df(story_id)
    for index, row in df.iterrows():
        with st.expander(f"{row['Comment'][0:50]} {index + 1} - Replies: {row['Replies']}"):
            st.write(row['Comment'])
