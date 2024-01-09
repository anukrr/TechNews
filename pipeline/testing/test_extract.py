''''Tests extract.py functions.'''
import pytest
from extract import get_top_stories, extract_story_info, generate_dataframe
import requests
import pandas

BASE_URL = "https://hacker-news.firebaseio.com/v0/"
STORY_COUNT = 200


def test_get_story_string():
    """Checks if invalid input type raises Error."""
    with pytest.raises(TypeError):
        get_top_stories('2')


def test_get_list_generated():
    """Tests list is returned."""
    assert isinstance(get_top_stories(10), list)


def test_returns_correct_elements():
    """Tests correct amount of elements in list."""
    assert len(get_top_stories(10)) == 10


def test_get_story_empty():
    """Tests exception raised when no input provided."""
    with pytest.raises(TypeError):
        get_top_stories()


def test_dict_returned():
    """Tests dictionary returned."""
    assert isinstance(extract_story_info(10), dict)


def test_get_info_string():
    """Tests exception raised when empty string provided."""
    with pytest.raises(AttributeError):
        extract_story_info(' ')


def test_get_info_empty():
    """Tests exception raised when no input provided."""
    with pytest.raises(TypeError):
        extract_story_info()

def test_df_generated():
    """Tests dataframe generated when correct input provided."""
    assert isinstance(generate_dataframe(5), pandas.core.frame.DataFrame)


def test_get_stories_success(requests_mock):
    """Test successful retrieval of stories from API."""

    requests_mock.get('https://hacker-news.firebaseio.com/v0/topstories.json',
                      status_code=200, json=[{}])

    get_top_stories(STORY_COUNT)

    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.method == "GET"
