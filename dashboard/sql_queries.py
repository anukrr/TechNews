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
