# Pipeline Directory

This directory contains the extract, transform and load script for the pipeline.
The pipeline tracks and stores information about the top 200 stories on the Hacker News API /topstores endpoint.

## Requirements
All requirements are stored in the requirements.txt file.

### Environment variables
Your `.env` should contain the following elements:
`DB_HOST`
`DB_PORT`
`DB_NAME`
`DB_USER`
`DB_PASSWORD`
`THRESHOLD` (the score increase limit per hour for viral stories)
`OPENAI_API_KEY`(used for the OpenAI API to generate `topics`.)
`GPT-MODEL` (GPT model of your choice. e.g.`GPT-MODEL=gpt-4-1106-preview`)

## `extract.py`
This script is for extracting important information about the stories directly from the HN API.

- `get_top_stories` this function returns a list of the top 200 story ids from the HN API.
- `extract_story_info` this finds important information about a story based on its id and returns it as a dictionary.
- `main` this function ties to the two previous functions together by converting information about each story in the list to a csv file 'all_stories.csv'.

## `transform.py`
This script formats the extracted information and removes invalid entries.

- `generate_topic` makes use of the openai library which provides access to the GPT API. It categorises a URL based on a set of given topics which have been decided upon by analysis of 200 urls with GPT4. It does this by making a request to the API with these specific instructions.
- `clean_dataframe` takes the data from the csv file as a pandas DataFrame so that it can be manipulated efficiently. Once all edits have been made it returns the cleaned dataframe.
