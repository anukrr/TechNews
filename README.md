# 🌐 Tech News Summariser 🌐


## Overview

The technology industry moves at an incredible pace with new advancements and updates being released each day. Keeping up to date with recent news and trending topics in the technology sector is a difficult task due to the high volume of news output each day.
This project aims to extract information from the Hacker News API, which contains news stories related to the technology sector.

## 🗃️ Repository Structure

This repository contains several directories, each with a specific functionality.

- `pipeline`: This contains the extract, transform and load scripts which make up the data pipeline. This pipeline continually extracts information from the Hacker News APIs in order to track the top 200 stories each hour and stores this information in an RDS database.

## Getting Started

Each repository contains a `README.md` file with instructions for that specific repository.

## Architecture Diagram

This section will contain the finalised diagram.
=======
psql -h <REMOTE HOST> -p <REMOTE PORT> -U <DB_USERNAME> -d <DB_NAME> 

DB_HOST=c9-tech-news.c57vkec7dkkx.eu-west-2.rds.amazonaws.com
c9-tech-news-db.c57vkec7dkkx.eu-west-2.rds.amazonaws.com
DB_PORT=5432
DB_NAME=
DB_USER=postgres
DB_PASSWORD=technews

psql -h c9-tech-news-db.c57vkec7dkkx.eu-west-2.rds.amazonaws.com -p 5432 -d tech_news -U postgres
psql -h c9-tech-news-db.c57vkec7dkkx.eu-west-2.rds.amazonaws.com -p 5432 -U postgres
