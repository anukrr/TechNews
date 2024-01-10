# Data Management Directory

This directory contains the python script that can archive week-old records into an s3 bucket for long-term storage.
The Dockerfile contains the instructions for setting up the Docker image for deployment as a Lambda function on AWS.

## Requirements
All requirements are stored in the requirements.txt file.

### Environment Variables
Your `.env` should contain the following elements:
Database Credentials:
`DB_HOST`
`DB_PORT`
`DB_NAME`
`DB_USER`
`DB_PASSWORD`
AWS Credentials:
`ACCESS_KEY_ID`
`SECRET_ACCESS_KEY`