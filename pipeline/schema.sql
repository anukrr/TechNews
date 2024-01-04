-- This file should contain all code required to create & seed database tables.
\c postgres
DROP DATABASE IF EXISTS technews;

CREATE DATABASE technews;
\c technews
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS stories;
DROP TABLE IF EXISTS topics;


CREATE TABLE topics (
  topic_id INT GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(250),
  PRIMARY KEY (topic_id)
);


INSERT INTO topics (name)
VALUES
('Programming & Software Development'),
('Game Development'),
('Algorithms & Data Structures'),
('Web Development & Browser Technologies'),
('Computer Graphics & Image Processing'),
('Operating Systems & Low-level Programming'),
('Science & Research Publications'),
('Literature & Book Reviews'),
('Artificial Intelligence & Machine Learning'),
('News & Current Affairs'),
('Miscellaneous & Interesting Facts');


CREATE TABLE stories (
  story_id INT, 
  title VARCHAR(250) NOT NULL,
  author VARCHAR(100) NOT NULL,
  story_url VARCHAR(500),
  creation_date TIMESTAMP NOT NULL,
  topic_id INT,
  PRIMARY KEY (story_id),
  CONSTRAINT fk_topic
    FOREIGN KEY (topic_id)
    REFERENCES topics(topic_id)
    ON DELETE CASCADE
  );


CREATE TABLE records (
  record_id INT GENERATED ALWAYS AS IDENTITY, 
  story_id INT NOT NULL,
  score SMALLINT NOT NULL,
  comments SMALLINT NOT NULL,
  record_time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY (record_id),
  CONSTRAINT fk_story
    FOREIGN KEY (story_id) 
    REFERENCES stories(story_id)
    ON DELETE CASCADE
  );
