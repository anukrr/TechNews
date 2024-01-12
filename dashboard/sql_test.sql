-- Average score
SELECT r.story_id, s.title, AVG(r.score) as average_score
FROM records r
JOIN stories s ON r.story_id = s.story_id
GROUP BY r.story_id, s.title;


-- LATEST RECORDS PAST HOUR
SELECT * from records
WHERE record_time >= NOW() - INTERVAL '1 hour';


-- 10 stories which have been in top stories the longest 

SELECT s.title,  t.name, COUNT(*) AS longest_stories
FROM records r
JOIN stories s ON r.story_id = s.story_id
JOIN topics t ON s.topic_id = t.topic_id
GROUP BY r.story_id, s.title, t.name
ORDER BY longest_stories DESC
LIMIT 10;


-- Average and median scores of all stories 
    -- All time average score
WITH AverageScores AS (
SELECT r.story_id, s.title, AVG(r.score) as average_score
FROM records r
JOIN stories s ON r.story_id = s.story_id
GROUP BY r.story_id, s.title
)
SELECT AVG(average_score) FROM AverageScores
;

    -- Avg score last hour
WITH latest_scores AS (
SELECT * from records
WHERE record_time >= NOW() - INTERVAL '1 hour')
SELECT AVG(score) FROM latest_scores
;

WITH latest_scores AS (
SELECT * from records
WHERE record_time >= (NOW() - INTERVAL '24 Hours') - INTERVAL '24 Hours')
SELECT AVG(score) FROM latest_scores
;

    -- Median all time
WITH AverageScores AS (
SELECT r.story_id, s.title, AVG(r.score) as average_score
FROM records r
JOIN stories s ON r.story_id = s.story_id
GROUP BY r.story_id, s.title
)
SELECT PERCENTILE_CONT(0.5) AS median_score WITHIN GROUP(ORDER BY average_score) FROM AverageScores;

    -- Median last hour
WITH latest_scores AS (
SELECT * from records
WHERE record_time >= NOW() - INTERVAL '1 hour')
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY score) AS median_score FROM latest_scores;


-- Author Contributions, most contributions/most popular

SELECT author, COUNT(*) as stories_created FROM stories
GROUP BY author
ORDER BY stories_created DESC
LIMIT 5;

SELECT author, story_url FROM stories
WHERE author LIKE 'PaulHoule'
ORDER BY story_url;


WITH latest_records AS (
SELECT DISTINCT ON (records.story_id)
    records.story_id, records.score
FROM records
ORDER BY records.story_id, records.record_time DESC)
SELECT s.author, SUM(latest_records.score) AS all_stories_total_votes FROM latest_records
JOIN stories s ON latest_records.story_id = s.story_id
GROUP BY s.author
ORDER BY all_stories_total_votes DESC
LIMIT 5;




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



SELECT s.title, r.record_time, r.score
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
ORDER BY r.story_id, r.record_time;


SELECT *
FROM records
WHERE story_id IN (
    SELECT r.story_id
    FROM records r
    WHERE r.record_time >= NOW() - INTERVAL '24 hours'
    GROUP BY r.story_id
    ORDER BY MAX(r.score) - MIN(r.score) DESC
    LIMIT 5
)
ORDER BY story_id, record_time;
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





WITH latest_scores AS (
SELECT * from records
WHERE record_time >= NOW() - INTERVAL '24 Hours')
SELECT AVG(score) FROM latest_scores
;