-- Average score
SELECT r.story_id, s.title, AVG(r.score) as average_score
FROM records r
JOIN stories s ON r.story_id = s.story_id
GROUP BY r.story_id, s.title;


-- 10 stories which have been in top stories the longest 
SELECT
    s.title,
    t.name,
    MIN(record_time) AS earliest_recording,
    MAX(record_time) AS most_recent_recording,
    EXTRACT(EPOCH FROM MAX(record_time) - MIN(record_time))/3600 AS time_difference_hours 
FROM records r
JOIN stories s ON r.story_id = s.story_id
JOIN topics t ON s.topic_id = t.topic_id
GROUP BY r.story_id, s.title, t.name
ORDER BY time_difference_hours DESC
LIMIT 10;


SELECT s.title,  t.name, COUNT(*) AS longest_stories
FROM records r
JOIN stories s ON r.story_id = s.story_id
JOIN topics t ON s.topic_id = t.topic_id
GROUP BY r.story_id, s.title, t.name
ORDER BY longest_stories DESC
LIMIT 10;


-- Sum all votes of all stories recorded per hour group (record time)

WITH HourlyVotes AS (
    SELECT
        EXTRACT(HOUR FROM record_time) AS hour_of_day,
        score,
        LAG(score) OVER (ORDER BY EXTRACT(HOUR FROM record_time)) AS prev_hour_score
    FROM
        records
)
SELECT
    hour_of_day,
    SUM(COALESCE(score - prev_hour_score, score)) AS score_diff
FROM
    HourlyVotes
GROUP BY
    hour_of_day
ORDER BY
    score_diff DESC;





SELECT
    EXTRACT(HOUR FROM record_time) AS hour_of_day,
    SUM(score) AS total_votes
FROM
    records
GROUP BY
    hour_of_day
ORDER BY
    total_votes DESC;


-- Average and median scores of all stories of all time
WITH AverageScores AS (
SELECT r.story_id, s.title, AVG(r.score) as average_score
FROM records r
JOIN stories s ON r.story_id = s.story_id
GROUP BY r.story_id, s.title
)
SELECT AVG(average_score) FROM AverageScores
;


WITH AverageScores AS (
SELECT r.story_id, s.title, AVG(r.score) as average_score
FROM records r
JOIN stories s ON r.story_id = s.story_id
GROUP BY r.story_id, s.title
)
SELECT PERCENTILE_CONT(0.5) AS median_score WITHIN GROUP(ORDER BY average_score) FROM AverageScores;

-- Author Contributions, most contributions/most popular


SELECT author, COUNT(*) as stories_created FROM stories
GROUP BY author
ORDER BY stories_created DESC
LIMIT 5;


WITH latest_records AS (
SELECT DISTINCT ON (records.story_id)
    records.story_id, records.score
FROM records
ORDER BY records.story_id, records.record_time DESC)
SELECT s.author, SUM(latest_records.score) AS all_stories_total_votes FROM latest_records
JOIN stories s ON latest_records.story_id = s.story_id
GROUP BY s.author
ORDER BY total_votes DESC
LIMIT 5;


-- TOP 5 Movers in last 24 hours
SELECT
    r.story_id, s.title,
    MAX(record_time) AS latest_timestamp,
    MAX(score) - MIN(score) AS vote_difference
FROM records r
JOIN stories s ON r.story_id = s.story_id
WHERE record_time >= NOW() - INTERVAL '24 hours'
GROUP BY r.story_id, s.title
ORDER BY vote_difference DESC
LIMIT 5;

-- Amount of New stories every hour

SELECT *
FROM (
    SELECT DISTINCT EXTRACT(HOUR FROM record_time) AS hour_of_day
    FROM records 
) hours
CROSS JOIN LATERAL (
    SELECT DISTINCT ON (story_id) *
    FROM records
    WHERE EXTRACT(HOUR FROM record_time) = hours.hour_of_day
    ORDER BY story_id, record_time DESC
) records;


SELECT
    EXTRACT(HOUR FROM record_time) AS hour_of_day,
    COUNT(*) AS new_story_count
FROM (
    SELECT DISTINCT ON (story_id)
        story_id,
        record_time
    FROM records
    ORDER BY story_id, record_time DESC
) AS latest_records
GROUP BY hour_of_day
ORDER BY new_story_count;


WITH last_day_records AS (
SELECT * FROM records
WHERE record_time >= NOW() - INTERVAL '24 hours'
)
SELECT
    EXTRACT(HOUR FROM record_time) AS hour_of_day,
    COUNT(*) AS new_story_count
FROM (
    SELECT DISTINCT ON (story_id)
        story_id,
        record_time
    FROM last_day_records
    ORDER BY story_id, record_time DESC
) AS latest_records
GROUP BY hour_of_day
ORDER BY new_story_count;
;


SELECT COUNT(*) FROM records
WHERE record_time >= NOW() - INTERVAL '24 hours';

SELECT COUNT(*) FROM
(SELECT DISTINCT ON (story_id) * FROM records
WHERE record_time >= NOW() - INTERVAL '24 hours') AS all_stories_previous_day;


-- Number of new stories in top stories over past 24
SELECT
    COUNT(DISTINCT story_id) AS unique_story_count
FROM records r1
WHERE NOT EXISTS (
    SELECT 1
    FROM records r2
    WHERE r1.story_id = r2.story_id
      AND r2.record_time < NOW() - INTERVAL '24 hours'
);


SELECT COUNT(story_id)
FROM (
    SELECT
        story_id,
        MIN(record_time) AS first_record_time
    FROM records
    GROUP BY story_id
) AS first_record_per_story
WHERE first_record_time >= NOW() - INTERVAL '24 hours';



