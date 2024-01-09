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


def get_parent_comment_ids(story: int) -> list:
    """Returns the id of comments from given story on Hacker News."""
    story_info = get(BASE_URL + f"{story}.json", timeout=30).json()
    comment_ids = story_info.get("kids")
    return comment_ids


def get_comment_text(comment: int) -> str:
    """Returns the text from a given comment."""

    comment_info = get(BASE_URL + f"{comment}.json", timeout=30).json()
    comment = comment_info.get("text")
    return comment


def get_comment_list(story: int):
    comments = get_parent_comment_ids(story)
    comment_list = [get_comment_text(comment) for comment in comments]
    return comment_list


def get_story_sentiment(story_id: str):
    """Performs sentiment analysis for a given story."""
    comment_list = get_comment_list(int(story_id))
    sentiment_list = []
    for comment in comment_list:
        blob = TextBlob(str(comment))
        for sentence in blob.sentences:
            sentiment = sentence.sentiment.polarity
        sentiment_list.append({'comment': comment,
                               'sentiment': sentiment})
    sentiment_mean = []
    for i in range(0, 20):
        sentiment_mean.append(sentiment_list[i]['sentiment'])
    average = sum(sentiment_mean)/len(sentiment_mean)
    return average


def generate_sentiment_gauge(value: int):
    """ """
    if -1 <= value < -0.6:
        category_color = "#FF0000"
        category_label = "Very Negative 😠"
    elif -0.6 <= value < -0.3:
        category_color = "#FFA500"
        category_label = "Negative 🙁"
    elif -0.3 <= value < 0.3:
        category_color = "#FFFF00"
        category_label = "Neutral 😐"
    elif 0.3 <= value < 0.6:
        category_color = "#8BFF00"
        category_label = "Positive 🙂"
    else:
        category_color = "#00FF00"
        category_label = "Very Positive 😄"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"Overall Sentiment: {category_label}"},
        gauge={'axis': {'range': [-1, 1]},
               'bar': {'color': category_color},
               }))

    return fig


def gauge_chart():
    '''Bar chart showing transaction count per truck.'''

    input_story_id = '38865518'

    value = get_story_sentiment(input_story_id)
    fig = generate_sentiment_gauge(value)
    # st.plotly_chart(sentiment_fig)
    return st.plotly_chart(fig)



# table to show comments thatcause most discussion 
def cycle_text(text_list, interval=5):
    index = 0
    while True:
        st.text(text_list[index])
        time.sleep(interval)
        index = (index + 1) % len(text_list)


def cycle_text(text_list, interval=2):
    index = 0
    text_container = st.empty()  # Create an empty container to hold the text

    while True:
        text_container.text(text_list[index])
        time.sleep(interval)
        index = (index + 1) % len(text_list)
    # while True:
    #     text = (text_list[index])
    #     time.sleep(interval)
    #     index = (index + 1) % len(text_list)


# st.markdown might let you add extra formattting vs st.text

if __name__ == "__main__":
    st.set_page_config(page_title="TechNews Dashboard",
                   page_icon=":bar_chart:", layout="wide")

    st.title(':truck: :moneybag: Truck Transactions :truck: :moneybag:')

    load_dotenv()
    gauge_chart()
    
    # st.text(f'')
    st.title("Cycling Text Box")

    text_list = ["Text 1", "Text 2", "Text 3"]
    cycle_text(text_list)

    # st.thread(target=cycle_text, args=(text_list,))
    # thread = threading.Thread(target=cycle_text, args=(text_list,))
    # thread.start()
        
