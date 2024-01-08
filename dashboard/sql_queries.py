"""Query commands used for niche analysis"""

LONGEST_LASTING_DF = """
    SELECT s.title,  t.name, COUNT(*) AS longest_stories
    FROM records r
    JOIN stories s ON r.story_id = s.story_id
    JOIN topics t ON s.topic_id = t.topic_id
    GROUP BY r.story_id, s.title, t.name
    ORDER BY longest_stories DESC
    LIMIT 10;
    """

COMMENTS = """SELECT story_id, comments, record_time FROM records;"""

MOST_AUTHOR_CONTRIBUTIONS = """SELECT author, COUNT(*) as stories_created FROM stories
GROUP BY author
ORDER BY stories_created DESC
LIMIT 5;"""

MOST_POPULAR_AUTHORS = """WITH latest_records AS (
SELECT DISTINCT ON (records.story_id)
    records.story_id, records.score
FROM records
ORDER BY records.story_id, records.record_time DESC)
SELECT s.author, SUM(latest_records.score) AS all_stories_total_votes FROM latest_records
JOIN stories s ON latest_records.story_id = s.story_id
GROUP BY s.author
ORDER BY all_stories_total_votes DESC
LIMIT 5;
"""


LAST_HOUR_AVERAGE_SCORE = """WITH latest_scores AS (
SELECT * from records
WHERE record_time >= NOW() - INTERVAL '1 hour')
SELECT AVG(score) FROM latest_scores
;
"""

LAST_HOUR_MEDIAN_SCORE = """WITH latest_scores AS (
SELECT * from records
WHERE record_time >= NOW() - INTERVAL '1 hour')
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY score) AS median_score FROM latest_scores;
"""