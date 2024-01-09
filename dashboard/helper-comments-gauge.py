"""Script containing helper functions for comment analysis sentiment gauge plot."""

import requests
from textblob import TextBlob
import plotly.graph_objects as go
import streamlit as st

BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"


def get_parent_comment_ids(story_id: int) -> list:
    """
    Returns the id of parent comments for a given story.
    Note: in this case the API endpoint considers parent comments as "kids" of a story.
    """
    story_info = requests.get(BASE_URL + f"{story_id}.json", timeout=30).json()
    return story_info.get("kids")  # Warning: see docstring


def get_comment_text(comment: int) -> str:
    """Returns the text from a given comment."""
    comment_info = requests.get(
        BASE_URL + f"{comment}.json", timeout=30).json()
    return comment_info.get("text")


def get_comment_list(story_id: int):
    comments = get_parent_comment_ids(story_id)
    return [get_comment_text(comment) for comment in comments]


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


def categorise_sentiment(sentiment_value: int):
    if -1 <= sentiment_value < -0.6:
        category_color = "#FF0000"
        category_label = "Very Negative 😠"
    elif -0.6 <= sentiment_value < -0.3:
        category_color = "#FFA500"
        category_label = "Negative 🙁"
    elif -0.3 <= sentiment_value < 0.3:
        category_color = "#FFFF00"
        category_label = "Neutral 😐"
    elif 0.3 <= sentiment_value < 0.6:
        category_color = "#8BFF00"
        category_label = "Positive 🙂"
    else:
        category_color = "#00FF00"
        category_label = "Very Positive 😄"

    return {'colour': category_color, 'label': category_label}


def generate_sentiment_gauge(sentiment_value: int):
    """"""
    category = categorise_sentiment(sentiment_value)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sentiment_value,
        title={'text': f"Overall Sentiment: {category.get('label')}"},
        gauge={'axis': {'range': [-1, 1]},
               'bar': {'color': category.get('colour')},
               }))

    return fig


def make_gauge_chart(input_story_id: int):
    '''Bar chart showing transaction count per truck.'''

    value = get_story_sentiment(input_story_id)
    fig = generate_sentiment_gauge(value)
    return st.plotly_chart(fig)


if __name__ == "__main__":

    input_story_id = 38865518

    st.title('Test gauge helper file \n')
    make_gauge_chart(input_story_id)
