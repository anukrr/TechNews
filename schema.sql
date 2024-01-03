-- This file should contain all code required to create & seed database tables.
\c postgres
DROP DATABASE IF EXISTS technews;

CREATE DATABASE technews;
\c technews
DROP TABLE IF EXISTS stories;
DROP TABLE IF EXISTS departments;

CREATE TABLE stories (
  story_id INT GENERATED ALWAYS AS IDENTITY, 
  title VARCHAR(250) NOT NULL,
  author VARCHAR(100) NOT NULL,
  story_url VARCHAR(250) NOT NULL,
  creation_date TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (story_id)
  );


CREATE TABLE departments (
  department_id SMALLINT GENERATED ALWAYS AS IDENTITY, 
  department_name VARCHAR(50) UNIQUE NOT NULL, 
  PRIMARY KEY (department_id)
  );


CREATE TABLE exhibitions (
  exhibit_id SMALLINT GENERATED ALWAYS AS IDENTITY,
  exhibit_name VARCHAR(50) NOT NULL,
  exhibit_description VARCHAR(250) NOT NULL,
  open_date TIMESTAMPTZ NOT NULL,
  floor_id INT NOT NULL,
  department_id INT NOT NULL,
  PRIMARY KEY (exhibit_id),
  CONSTRAINT fk_floor 
    FOREIGN KEY (floor_id) 
    REFERENCES floors (floor_id)
    ON DELETE CASCADE,
  CONSTRAINT fk_department 
    FOREIGN KEY (department_id) 
    REFERENCES departments (department_id)
    ON DELETE CASCADE
  );


CREATE TABLE emergency_events (
  emergency_id SMALLINT GENERATED ALWAYS AS IDENTITY, 
  created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
  exhibit_id SMALLINT NOT NULL,
  PRIMARY KEY (emergency_id),
  CONSTRAINT fk_emergency 
    FOREIGN KEY (exhibit_id) 
    REFERENCES exhibitions(exhibit_id)
    ON DELETE CASCADE
  );


CREATE TABLE assistance_events (
  assistance_id SMALLINT GENERATED ALWAYS AS IDENTITY, 
  created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
  exhibit_id SMALLINT NOT NULL,
  PRIMARY KEY (assistance_id),
  CONSTRAINT fk_assistance 
    FOREIGN KEY (exhibit_id) 
    REFERENCES exhibitions(exhibit_id)
    ON DELETE CASCADE
  );
