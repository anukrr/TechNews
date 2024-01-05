-- Average score
SELECT r.story_id, s.title, AVG(r.score) as average_score
FROM records r
JOIN stories s ON r.story_id = s.story_id
GROUP BY r.story_id, s.title;


-- 10 stories which have lasted the longest 
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


SELECT s.title,  t.name,  AS longest_stories
FROM records r
JOIN stories s ON r.story_id = s.story_id
JOIN topics t ON s.topic_id = t.topic_id
GROUP BY r.story_id, s.title, t.name



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