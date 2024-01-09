import re
import html
import time
import threading
import streamlit as st
from requests import get
import pandas as pd

BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"
CLEANR = re.compile('<.*?>')


def get_comment_ids(story: int) -> list:
    story_info = get(BASE_URL + f"{story}.json", timeout=30).json()
    comment_ids = story_info.get("kids")
    return comment_ids


def format_html(text_string: str):
    unescaped_text = html.unescape(text_string)
    clean_text = re.sub(CLEANR, '', unescaped_text)
    return clean_text


def get_top_5_most_replied_parent_comments(story_id: int):
    parent_comments = get_comment_ids(story_id)

    parent_comments_list = []
    for parent_comment_id in parent_comments:
        comment_info = get(
            BASE_URL + f"{parent_comment_id}.json", timeout=30).json()
        comment_text = comment_info.get("text")
        comment_title = format_html(
            comment_text) if comment_text else "No title available"
        number_of_children = 0
        kids_info = comment_info.get("kids")
        if kids_info is not None:
            number_of_children = len(kids_info)

        parent_comments_list.append(
            {'title': comment_title, 'number_of_children': number_of_children}) # add user name as well

    sorted_list = sorted(parent_comments_list, key=lambda comment_dict: comment_dict.get(
        'number_of_children', 0), reverse=True) 
    return sorted_list[:5]


# def cycle_text(text_list, interval=4):
#     index = 0
#     box = st.empty()
#     while True:
#         box.write(f'{text_list[index]}')  # st.text(text_list[index])
#         time.sleep(interval)
#         index = (index + 1) % len(text_list)

# def get_string_list():
#     # add user too
#     return [f"{parent_comment.get('title')} \n\n [{parent_comment.get('number_of_children')} replies]" for parent_comment in top_5_comments]

def generate_comments_df(top_comments: list) -> pd.DataFrame:
    """"""
    data = get_top_5_most_replied_parent_comments(38865518)
    df = pd.DataFrame(data)
    columns = ['Comment', 'Replies'] # add user column
    df.columns = columns
    return df

if __name__ == "__main__":
    st.subheader('URL NLP analysis', divider='rainbow') # need to error filter for URLs not found at hackernews
    url = st.text_input('Enter a URL', 'url')
    st.write('Article', url)

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
        # align replies to right side
        # add poster username too
 


    
