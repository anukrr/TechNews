"""Query commands used for niche analysis"""

LONGEST_LASTING_DF = """
    SELECT s.title,  t.name, COUNT(*) AS longest_stories
    FROM records r
    JOIN stories s ON r.story_id = s.story_id
    JOIN topics t ON s.topic_id = t.topic_id
    GROUP BY r.story_id, s.title, t.name
    ORDER BY longest_stories DESC
    LIMIT 5;
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

RECENT_NEW_ENTRIES = """SELECT
    COUNT(DISTINCT story_id) AS unique_story_count
FROM records r1
WHERE NOT EXISTS (
    SELECT 1
    FROM records r2
    WHERE r1.story_id = r2.story_id
      AND r2.record_time < NOW() - INTERVAL {}
);"""

PREVIOUS_NEW_ENTRIES = """SELECT
    COUNT(DISTINCT story_id) AS unique_story_count
FROM records r1
WHERE NOT EXISTS (
    SELECT 1
    FROM records r2
    WHERE r1.story_id = r2.story_id
      AND r2.record_time < (NOW() - INTERVAL {}) - INTERVAL {}
);"""



RECENT_AVERAGE_SCORE = """WITH latest_scores AS (
SELECT * from records
WHERE record_time >= NOW() - INTERVAL {})
SELECT AVG(score) FROM latest_scores
;
"""

PREVIOUS_AVERAGE_SCORE = """WITH latest_scores AS (
SELECT * from records
WHERE record_time >= (NOW() - INTERVAL {}) - INTERVAL {})
SELECT AVG(score) FROM latest_scores
;
"""

RECENT_MEDIAN_SCORE = """WITH latest_scores AS (
SELECT * from records
WHERE record_time >= NOW() - INTERVAL {})
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY score) AS median_score FROM latest_scores;
"""

PREVIOUS_MEDIAN_SCORE = """WITH latest_scores AS (
SELECT * from records
WHERE record_time >= (NOW() - INTERVAL {}) - INTERVAL {})
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY score) AS median_score FROM latest_scores;
"""

FIVE_BIGGEST_MOVERS = """SELECT s.title, r.record_time, r.score
FROM records r
JOIN stories s ON r.story_id = s.story_id
WHERE r.story_id IN (
    SELECT r.story_id
    FROM records r
    JOIN stories s ON r.story_id = s.story_id
    WHERE r.record_time >= NOW() - INTERVAL '24 hours'
    GROUP BY r.story_id, s.title
    ORDER BY MAX(r.score) - MIN(r.score) DESC
    LIMIT 5
)
ORDER BY r.story_id, r.record_time;"""


VOTES_BY_HOUR = """
    SELECT
        EXTRACT(HOUR FROM record_time) AS hour_of_day,
        SUM(score) AS total_votes
    FROM
        records
    GROUP BY
        hour_of_day
    ORDER BY
        total_votes DESC;
    """