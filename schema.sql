-- This file should contain all code required to create & seed database tables.
\c postgres
DROP DATABASE IF EXISTS technews;

CREATE DATABASE technews;
\c technews
DROP TABLE IF EXISTS stories;
DROP TABLE IF EXISTS records;


CREATE TABLE stories (
  story_id INT, 
  title VARCHAR(250) NOT NULL,
  author VARCHAR(100) NOT NULL,
  story_url VARCHAR(500) NOT NULL,
  creation_date TIMESTAMP NOT NULL,
  PRIMARY KEY (story_id)
  );


CREATE TABLE records (
  record_id INT GENERATED ALWAYS AS IDENTITY, 
  story_id INT NOT NULL,
  score SMALLINT NOT NULL,
  comments INT NOT NULL,
  record_time TIMESTAMP NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY (record_id),
  CONSTRAINT fk_story
    FOREIGN KEY (story_id) 
    REFERENCES stories(story_id)
    ON DELETE CASCADE
  );
