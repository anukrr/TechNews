"""Script tests functions in transform.py."""
import pytest
import pandas as pd
from transform import clean_dataframe



data = {
    "time": [1704442250, 1704449007],
    "descendants": [10, None],
    "by": ["rodarima", "noteness"],
    "url": ["https://abagames.github.io/crisp-game-lib-11-games/?pakupaku", "https://github.com/kspalaiologos/malbolge-lisp"],
    "type": ['story', 'comment']
}

def test_clean_time_success():
    """Tests base case of success for clean_data function."""
    sample_df = pd.DataFrame(data)
    sample_df = clean_dataframe(sample_df)
    assert str(sample_df["creation_date"][0]) == '2024-01-05 08:10:50'

def test_ket_name_changes():
    "Tests base case of dataframe key name changes."
    sample_df = pd.DataFrame(data)
    sample_df = clean_dataframe(sample_df)
    assert (str(sample_df.keys())) == "Index(['creation_date', 'comments', 'author', 'story_url', 'topic_id'], dtype='object')"

def test_clean_wrong_input():
    """Tests exception raised if wrong input type provided."""
    with pytest.raises(Exception):
        clean_dataframe('df')


def test_clean_empty_input():
    """Tests exception raised if no input provided."""
    with pytest.raises(Exception):
        clean_dataframe()



def test_clean_int_input():
    """Tests exception raised if wrong input type provided."""
    with pytest.raises(Exception):
        clean_dataframe(1234)

def test_clean_partial_empty_df():
    """Tests exception raised if input dataframe is partially empty."""
    with pytest.raises(Exception):
        faulty_data = {
            "time": [],
            "descendants": [10, None],
            "by": ["rodarima", "noteness"],
            "url": ["https://abagames.github.io/crisp-game-lib-11-games/?pakupaku", "https://github.com/kspalaiologos/malbolge-lisp"],
            "type": ['story', 'comment']
        }
        sample_df = pd.DataFrame(faulty_data)
        sample_df = clean_dataframe(sample_df)
        clean_dataframe(sample_df)

def test_clean_empty_df():
    """Tests exception raised if empty dataframe provided as input."""
    with pytest.raises(Exception):
        faulty_data = {"": ""}
        sample_df = pd.DataFrame(faulty_data)
        sample_df = clean_dataframe(sample_df)
        clean_dataframe(sample_df)
