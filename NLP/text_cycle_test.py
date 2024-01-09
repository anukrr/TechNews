import re
import html
import time
import threading
import streamlit as st
from requests import get


BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"
CLEANR = re.compile('<.*?>')


def get_comment_ids(story: int) -> list:
    """Returns the id of comments from given story on Hacker News."""
    story_info = get(BASE_URL + f"{story}.json", timeout=30).json()
    comment_ids = story_info.get("kids")
    return comment_ids


def format_html(text_string: str):
    # Unescape HTML entities and remove HTML tags
    return re.sub(CLEANR, '', html.unescape(text_string))


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
####WORKING CYCLE TEXT
def cycle_text(text_list, interval=4):
    index = 0
    box = st.empty()
    while True:
        box.write(f'{text_list[index]}')
        # st.text(text_list[index])
        time.sleep(interval)
        index = (index + 1) % len(text_list)



if __name__ == "__main__":

    st.title("Cycling Text Box")

    text_list = ['> efficiently converts optical power to electrical powerDamn, I thought it was just  - - - [8 replies]',
                 'So... I have a really interesting anecdote on "Power over fiber"In ~20 - - - [5 replies]',
                 'From a reply:  “wow. I expected expensive (two digits), but indeed: these are _very_ expen - - - [4 replies]',
                 'How much optical power could be safely carried over such an optical fiber in theory? What  - - - [4 replies]',
                 "What's the use-case here? That's the biggest optoisolator I've ever heard o - - - [4 replies]"]
    cycle_text(text_list)
    

    # st.thread(target=cycle_text, args=(text_list,))
    # thread = threading.Thread(target=cycle_text, args=(text_list,))
    # thread.start()