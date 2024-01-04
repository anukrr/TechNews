''''Tests extract.py functions.'''
import pytest
from unittest.mock import patch
import requests_mock
import requests
from extract import get_top_stories, extract_story_info

BASE_URL = "https://hacker-news.firebaseio.com/v0/"
STORY_COUNT =200

def test_get_story_string():
    with pytest.raises(TypeError):
        get_top_stories('2')


def test_get_story_empty():
    with pytest.raises(TypeError):
        get_top_stories(' ')


def test_get_info_string():
    with pytest.raises(Exception):
        extract_story_info('2')


def test_get_info_empty():
    with pytest.raises(Exception):
        extract_story_info(' ')





def test_get_stories_success(requests_mock):
    """Test successful retrieval of stories from API."""

    requests_mock.get(f"{BASE_URL}topstories.json",
                        status_code=200, json=[{}])

    get_top_stories(STORY_COUNT)

    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.method == "GET"
