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


### API Usage
The Hacker News API has base url `https://hacker-news.firebaseio.com/v0/`, and three endpoints for live story data:
- `/v0/newstories` - 500 latest stories to be added (also contains jobs).
- `/v0/topstories` - Up to 500 top and new stories (also contains jobs).
    - uses Hacker News own algorithm to rank stories based on the `score` and time elapsed since creation `time`.
- `/v0/beststories` - 200 stories with the highest score in a fixed timescale (possibly the last 3 days).

e.g. `https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty`

### Choosing to work with data from `/v0/topstories`
We chose to extract data from the `/v0/topstories` endpoint at regular intervals. 
This would let us automatically filter our input data to only contain stories with a required minimum level of activity. 
- It is observable that the vast majority of posts are simply links to articles that get no response at all.Continually extracting every story added, using the `/v0/newstories` endpoint, means we would end up populating the database with a large quantity of "dud" stories. These dud stories offer no meaningful insight, slow database operations and therefore require filtering out.
- On the other hand, it can be observed that it takes very little traction for a story to become available at `/v0/topstories`. In fact, stories with not even 10 votes in a few hours can make the top 20 ranked stories at `/v0/topstories`. This means the `/v0/topstories` endpoint acts a convenient filter, helping us to easily identify the stories that get any traction at all.

### Why not track each story by it's id? Why track using just the `/v0/topstories` endpoint?
When a story enters the rankings at the `/v0/topstories` endpoint it signifies some traction, so we choose add its record to our database. However from this point onwards, we do not track each story in our database using its  unique `id`. Instead we choose to add subsequent sets of records by continuing to extract only those stories present at the `/v0/topstories` endpoint - accepting the possibility that a previously tracked story may lose traction and fall out of the data held at `/v0/topstories`.
- Tracking all the stories that enter our database individually (using their unique `id`s) would mean that we would would be forced to keep tracking them indefinitely, even after they lose traction.
- Tracking all the stories that enter our database individually would also require looping through the specific endpoint for each story (e.g. `https://hacker-news.firebaseio.com/v0/item/<story_id>.json?print=pretty`). This would be significantly slower that taking a single "snapshot" of the `/v0/topstories` endpoint data.
- Bearing in mind that it takes very little activity to remain in the top stories rankings, we assume that a story that cannot maintain traction in subsequent hours is not active enough to be considered for the purposes of growth or virality.
- All stories will fall out of the rankings at `/v0/topstories` at some point. This means they will stop being extracted to our database after that point too. This is a deliberate design feature. Being able to see when this happens lets us draw useful insights as to why some stories might not "take off" and also analyse which types of stories continue to draw interest, and for how long.