import re
import pprint
from bs4 import BeautifulSoup
import html
from os import environ
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import streamlit as st
from requests import get
import json
import textblob
from textblob import TextBlob
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = 'plotly'
import time
import threading


BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"
CLEANR = re.compile('<.*?>')


def get_comment_ids(story: int) -> list:
    """Returns the id of comments from given story on Hacker News."""
    story_info = get(BASE_URL + f"{story}.json", timeout=30).json()
    comment_ids = story_info.get("kids")
    return comment_ids


def format_html(text_string: str):
    # Unescape HTML entities
    unescaped_text = html.unescape(text_string)
    # use regex to get rid of html tags
    clean_text = re.sub(CLEANR, '', unescaped_text)
    return clean_text


def get_top_5_most_replied_parent_comments(story_id: int):
    # get all its parent comments
    parent_comments = get_comment_ids(story_id)

    parent_comments_list = []
    for parent_comment_id in parent_comments:
        # figure out a comment's title
        comment_info = get(
            BASE_URL + f"{parent_comment_id}.json", timeout=30).json()

        # Check if "text" key exists in comment_info
        comment_text = comment_info.get("text")
        comment_title = format_html(
            comment_text[:60]) if comment_text else "No title available"

        # figure out the number of children it has
        number_of_children = 0
        kids_info = comment_info.get("kids")
        if kids_info is not None:
            number_of_children = len(kids_info)

        # list of dicts where each dictionary is: {parent_comment_id : number_of_children}
        parent_comments_list.append(
            {'title': comment_title, 'number_of_children': number_of_children})

    # sort list of dicts by number_of_children
    sorted_list = sorted(parent_comments_list, key=lambda comment_dict: comment_dict.get(
        'number_of_children', 0), reverse=True)
    return sorted_list[:5]


# table to show comments thatcause most discussion 
def cycle_text(text_list, interval=4):
    index = 0
    while True:
        st.text(text_list[index])
        time.sleep(interval)
        index = (index + 1) % len(text_list)



if __name__ == "__main__":

    st.title("Cycling Text Box")


    text_list = ['text','text2','text3']
    cycle_text(text_list)
    

    # st.thread(target=cycle_text, args=(text_list,))
    # thread = threading.Thread(target=cycle_text, args=(text_list,))
    # thread.start()