# Email Lambda Directory
This contains the necessary components to deploy and run a script on AWS Lambda that can summarises the fastest growing stories from the HN API.
A stories `score_change` is calculated by the score increase over the last 24 hours. The OpenAI API is used to summarise the content of attached URLs for the top X posts and they are sent in an email newsletters to subscribers. 

# Setup
### Requirements
All requirements are stored in the requirements.txt file.

### Environment variables
Your `.env` should contain the following elements:
`DB_HOST`
`DB_PORT`
`DB_NAME`
`DB_USER`
`DB_PASSWORD`
`THRESHOLD` (the score increase limit per hour for viral stories)
`OPENAI_API_KEY`
`GPT-MODEL` (model of your choice. e.g.`GPT-MODEL=gpt-4-1106-preview`)