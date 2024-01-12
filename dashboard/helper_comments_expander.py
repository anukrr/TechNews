"""Helper script containing functions for comment expander (comment analysis)."""

import re
import html
import streamlit as st
import requests
import pandas as pd

BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"
CLEANR = re.compile('<.*?>')


def get_parent_comment_ids(story_id: int) -> list:
    """Returns the id of parent comments for a given story.
    Note: in this case the API endpoint considers parent comments as "kids" of a story."""
    story_info = requests.get(BASE_URL + f"{story_id}.json", timeout=30).json()
    return story_info.get("kids")


def format_html(text_string: str):
    """Cleans and formats html text."""
    clean_text = re.sub(CLEANR, '', html.unescape(text_string))
    return clean_text


def get_top_5_most_replied_parent_comments(story_id: int):
    """Takes in a story_id. Returns a list of the top parent comments."""
    parent_comments = get_parent_comment_ids(story_id)

    parent_comments_list = []
    for parent_comment_id in parent_comments:
        comment_info = requests.get(
            BASE_URL + f"{parent_comment_id}.json", timeout=30).json()

        comment_text = comment_info.get("text")
        comment_title = format_html(
            comment_text) if comment_text else "No title available"
        comment_user = comment_info.get("by")

        number_of_children = 0
        kids_info = comment_info.get("kids")
        if kids_info is not None:
            number_of_children = len(kids_info)

        parent_comments_list.append(
            {'title': comment_title,
             'user': comment_user,
             'number_of_children': number_of_children})

    sorted_list = sorted(parent_comments_list, key=lambda comment_dict: comment_dict.get(
        'number_of_children', 0), reverse=True)
    return sorted_list[:5]


def generate_comments_df(top_comments: list[dict]) -> pd.DataFrame:
    """Takes in a list of the top comments and returns key info as a dataframe. """
    df = pd.DataFrame(top_comments)
    columns = ['Comment', 'User', 'Replies']
    df.columns = columns
    return df


def make_expander(story_id: int) -> None:
    """Takes in a story_id and writes streamlit expander boxes."""
    top_5_comments = get_top_5_most_replied_parent_comments(story_id)
    df = generate_comments_df(top_5_comments)

    for index, row in df.iterrows():
        with st.expander(f"{row['Comment'][0:60]} - - - [Replies: {row['Replies']}]"):
            st.write(row['Comment'])
            st.write(f"({row['User']})")
