# Design Choices Notes
The contents of this file should be incorporated into the README.

## Pipeline
### API Usage
The Hacker News API has base url `https://hacker-news.firebaseio.com/v0/`, and three endpoints for live story data:
- `/v0/newstories` - 500 latest stories to be added (also contains jobs).
- `/v0/topstories` - Up to 500 top and new stories (also contains jobs).
    - uses Hacker News own algorithm to rank stories based on the `score` and time elapsed since creation `time`.
- `/v0/beststories` - 200 stories with the highest score in a fixed timescale (possibly the last 3 days).

e.g. `https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty`

