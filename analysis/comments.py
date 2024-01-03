"""This script extracts comments from the Hacker News API."""
import pandas as pd
from requests import get
from html import unescape
import re



BASE_URL = "https://hacker-news.firebaseio.com/v0/item"
STORY_COUNT = 200


def clean_API_text(comment: str) -> str:
    input_string = "\"Nice! Playing around with the widget under the section &quot;Experimenting with lines&quot; I&#x27;m reminded of Bret Victor&#x27;s Inventing on Principle talk [0] (an absolute must watch, if anyone hasn&#x27;t yet). In particular, changing the smoothness reveals a sort of scaling effect that I&#x27;d probably never know about if not playing around with sliders and having it update in real time rather than setting individual values. Very interesting and beautiful!<p>[0] <a href=\"https:&#x2F;&#x2F;youtu.be&#x2F;PUv66718DII?si=2urxGUwD_lWA8C4q\" rel=\"nofollow\">https:&#x2F;&#x2F;youtu.be&#x2F;PUv66718DII?si=2urxGUwD_lWA8C4q</a>\""

# Replace HTML entities and convert the string to HTML
    html_text = unescape(input_string)

      

def get_comments(story: int) -> dict:
    """Returns the comments of the top 200 stories on Hacker News."""
    top_stories = get(BASE_URL + f"{story}.json", timeout=30).json()
    return top_stories[:count]
