# Text Lambda Directory

This contains the necessary components to deploy and run a script on AWS Lambda that can detect viral stories from the HN API.
A stories virality is calculated by the score increase over the space of an hour, and if it is above a certain threshold the an SMS is sent to those subscribed to this service. The subscriber will receive a message containing the story title and url of any story that meets this criteria.

## Requirements

All requirements are stored in the requirements.txt file.
Environment variables requires as follows:
Database Credentials:
`DB_HOST`
`DB_PORT`
`DB_NAME`
`DB_USER`
`DB_PASSWORD`
AWS Credentials:
`ACCESS_KEY_ID`
`SECRET_ACCESS_KEY`
Other Variables:
`THRESHOLD` (the score increase limit per hour for viral stories)

## `text_lambda.py`

This is the functional script that runs at regular intervals to assess story virality and notify subscribers.

- `viral_checker` this function takes in threshold (score increase minimum to be classified as viral) and story_limit with corresponds to the amount of stories that are to be tested. The main viral_query extracts the story ids of any story exceeding the threshold and a further story_info_query finds the details from these story ids. It returns a list of the stories in dictionary form.
- `lambda_handler` this is the main lambda body which is activated each hour. It makes use of the `viral_checker` and if there are viral stories returned, it will generate a text message with details about these stories and send them.