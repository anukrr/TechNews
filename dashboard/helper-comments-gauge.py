"""Script containing helper functions for comment analysis sentiment gauge plot."""

import requests
from textblob import TextBlob
import plotly.graph_objects as go
import streamlit as st

BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"


def get_parent_comment_ids(story: int) -> list:
    """
    Returns the id of comments from given story on Hacker News.
    """
    story_info = requests.get(BASE_URL + f"{story}.json", timeout=30).json()
    comment_ids = story_info.get("kids")  # Warning: read
    return comment_ids


def get_comment_text(comment: int) -> str:
    """Returns the text from a given comment."""
    comment_info = requests.get(
        BASE_URL + f"{comment}.json", timeout=30).json()
    comment = comment_info.get("text")
    return comment


def get_comment_list(story: int):
    comments = get_parent_comment_ids(story)
    comment_list = [get_comment_text(comment) for comment in comments]
    return comment_list


def get_story_sentiment(story_id: int):
    """Performs sentiment analysis for a given story."""
    comment_list = get_comment_list(story_id)
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


def make_gauge_chart(input_story_id: int):
    '''Bar chart showing transaction count per truck.'''

    value = get_story_sentiment(input_story_id)
    gauge_fig = generate_sentiment_gauge(value)
    # st.plotly_chart(sentiment_fig)
    return st.plotly_chart(gauge_fig)


if __name__ == "__main__":

    input_story_id = 38865518

    st.title('Test gauge helper file \n')
    make_gauge_chart(input_story_id)
