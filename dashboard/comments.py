"""This script extracts comments from the Hacker News API."""
from requests import get


BASE_URL = "https://hacker-news.firebaseio.com/v0/item/"


def clean_API_text(comment: str) -> str:
    # Replace HTML entities and convert the string to HTML
    input_string = "\"Nice! Playing around with the widget under the section &quot;Experimenting with lines&quot; I&#x27;m reminded of Bret Victor&#x27;s Inventing on Principle talk [0] (an absolute must watch, if anyone hasn&#x27;t yet). In particular, changing the smoothness reveals a sort of scaling effect that I&#x27;d probably never know about if not playing around with sliders and having it update in real time rather than setting individual values. Very interesting and beautiful!<p>[0] <a href=\"https:&#x2F;&#x2F;youtu.be&#x2F;PUv66718DII?si=2urxGUwD_lWA8C4q\" rel=\"nofollow\">https:&#x2F;&#x2F;youtu.be&#x2F;PUv66718DII?si=2urxGUwD_lWA8C4q</a>\""


def get_comment_ids(story: int) -> list:
    """Returns the id of comments from given story on Hacker News."""
    story_info = get(BASE_URL + f"{story}.json", timeout=30).json()
    comment_ids = story_info.get("kids")
    return comment_ids


def get_comments(comment: int) -> str:
    """Returns the text from a given comment."""

    comment_info = get(BASE_URL + f"{comment}.json", timeout=30).json()
    comment = comment_info.get("text")
    return comment


if __name__ == "__main__":
    comments = (get_comment_ids(38865518))

    for comment in comments:
        print(get_comments(comment))