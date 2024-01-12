"""Lamnda function to send daily summary emails."""

from os import environ
from datetime import date
import json
import logging
from dotenv import load_dotenv
import pandas as pd
import boto3
import psycopg2
import openai
from botocore.config import Config


DATE_TODAY = date.today().strftime("%A %B %d %Y")


def handle_openai_errors(err):
    """OpenAI API request error-handling as per official docs."""
    if isinstance(err, openai.APIError):
        logging.exception("OpenAI API returned an API Error: %s", err)
    elif isinstance(err, openai.APIConnectionError):
        logging.exception("Failed to connect to OpenAI API: %s", err)
    elif isinstance(err, openai.RateLimitError):
        logging.exception("OpenAI API request exceeded rate limit: %s", err)
    else:
        logging.exception("Unexpected error: %s", err)
    raise err


def get_db_connection():
    """Returns a database connection."""
    try:
        return psycopg2.connect(
            host=environ["DB_HOST"],
            port=environ["DB_PORT"],
            database=environ["DB_NAME"],
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"]
            )
    except psycopg2.OperationalError as error:
        logging.exception("Error connecting to the database: %s", error)
        raise


def load_stories_data() -> pd.DataFrame:
    """Loads stories with greatest score change over last 24hrs from RDS.
    Returns them as a Dataframe object."""
    query = """
            SELECT
                records.story_id,
                MAX(score) - MIN(score) AS score_change,
                stories.title,
                stories.story_url,
                MAX(record_time) AS latest_update,
                stories.creation_date
            FROM records
            JOIN stories ON records.story_id = stories.story_id
            WHERE record_time >= NOW() - INTERVAL '24 hours'
            GROUP BY records.story_id, stories.title, stories.story_url, stories.creation_date
            ORDER BY score_change
                DESC LIMIT 5
            ;
            """
    return pd.read_sql(query, con=get_db_connection())


def get_url_list(dataframe: pd.DataFrame) -> list:
    """Gets a list of story URLs from a dataframe."""
    return dataframe['story_url'].to_list()


def summarise_stories(url_list:list[str]) -> str: # not sure the type of the output here
    """Uses the OpenAI API to generate summaries for a list of URLs."""
    system_content_spec = """You are a newsletter writer, producing summarised news articles similar to this:The days of empty car dealer lots and high sticker prices may be in the US auto industry’s rearview mirror.
                        Following a 2023 sales rebound, industry analysts predict a “return to 
                        normalcy” in the US car market, 
                        according to a new report from Cox Automotive.
                        The momentum of 2023 ended in a Q4 milestone in the EV race: Chinese EV 
                        maker BYD unseated Tesla as the world’s top all-electric vehicle seller. Tesla had a strong quarter, notching a record 
                        484,500 deliveries globally. But BYD clinched the top spot with some 526,000 all-electric vehicle sales in Q4.
                        In the US, analysts expect EV sales to grow in 2024, though likely at a
                         slower pace than they did in 2023.
                        “We’re right back to where we were as an industry” before the pandemic, 
                        Charlie Chesbrough, Cox Automotive’s senior economist, told Tech Brew. “Inventories are 
                        starting to build again. Dealer lots are starting to get full again. And discounting and incentives are back in full force.”."""
    user_content_spec = f"""Write a summary approximately 200 words in length,
                        that gives key insights for articles in list: {url_list},
                        return ONLY a string containing a list of dictionaries with keys 'article_title' which
                        includes the name of the article and 'summary'."""

    client = openai.OpenAI(api_key=environ["OPENAI_API_KEY"])
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            messages=[
                {"role": "system", "content": system_content_spec},
                {"role": "user", "content": user_content_spec}],
            temperature=1
            )
        return response.choices[0].message.content.strip()
    except openai.APIError as error:
        return handle_openai_errors(error)


def generate_summaries_dict() -> dict:
    """Creates a dictionary containing all"""
    top_stories = load_stories_data()
    top_url_list = get_url_list(top_stories)
    summaries = summarise_stories(top_url_list)
    return json.loads(f"{summaries}")


def make_article_box_html(article: dict) -> str:
    """Takes in an article and returns a html string encapsulating the details of each article."""
    return f"""<body style="border-width:3px;
                     border-style:solid; border-color:#E6E6FA;
                     border-radius: 12px;
                     padding: 20px;
                     border-spacing: 10px 2em;">
       <h2 style="color: #008B8B;">{article.get('article_title')}</h2>
       <p style="color:#6495ED">{article.get('summary')}</p>  <div>
        <p style="margin-bottom:0;">
            <a hred={article.get('story_url')}> Read Article </a> |
            <p> "{article.get('creation_date')}" </p> |
            <p> "{article.get('author')}" </p>
            </div></body>"""


def generate_html_string(dict_of_summary: list[dict], df) -> str:
    '''Generates HTML string for the email.'''
    html_start = f"""<html>
    <head>
    </head>
    <body>
    <center class="wrapper">
        <table class="main" width="700">
        <tr>
            <td height="8" style="background-color: #F0F8FF;">
            </td>
            </tr>
    <h1> Daily Brief</h1>
    <h1 style="color:#5F9EA0">Top Stories</h1>"""

    html_end="""</body>
        </table>
    </center>
    </body>
    </html>"""
    articles_list = []
    
    for i in range(0,5):
        title = df.loc[i].get('title')
        summary = dict_of_summary[i].get('summary')
        creation_date = df.loc[i].get('creation_date')
        creation_date = creation_date.strftime("%d/%m/%Y")
        story_url = df.loc[i].get('story_url')
        # corrected_date = creation_date.strftime("%d/%m/%Y")

        article_box = f"""<div style="border-width:3px; border-style:solid; border-color:#E6E6FA; border-radius: 12px; padding: 20px; border-spacing: 10px 2em; margin: 10px">
        <h2 style="color: #008B8B;"> {title}</h2>
        <p style="color:#6495ED"> {summary} </p>
        <div>
        <p style="margin-bottom:0;">
            <a href="{story_url}"> Read Article </a> |
            <a"> {creation_date} </a> |
            </div>
            </div>"""
        articles_list.append(article_box)
    articles_string = " ".join(articles_list)
    html_full = html_start + articles_string + html_end
    return html_full


def send_email(html_string: str):
    """Sends email newsletter using generated html string."""

    client = boto3.client('ses',
                          region_name='eu-west-2',
                          aws_access_key_id=environ["ACCESS_KEY_ID"],
                          aws_secret_access_key=environ["SECRET_ACCESS_KEY"],
                          config=Config(connect_timeout=5, read_timeout=60, retries={'max_attempts': 5}))

    response = client.send_email(
        Destination={
                'ToAddresses': ['trainee.anurag.kaur@sigmalabs.co.uk',
                                # 'trainee.kevin.chirayil@sigmalabs.co.uk',
                                # 'trainee.kayode.apena@sigmalabs.co.uk',
                                # 'trainee.jack.hayden@sigmalabs.co.uk',
                                # more?
                                ]
                # might need everyone added as a BccAddress instead (see docs)
            },
        Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': html_string
                    }
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': f'Daily Brief {DATE_TODAY}',
                },
            },
        Source='trainee.anurag.kaur@sigmalabs.co.uk'
    )

    return response


def handler(event=None, context=None):
    """Handler function."""
    load_dotenv()
    summaries_dict = generate_summaries_dict()
    df = load_stories_data()
    html_str = generate_html_string(summaries_dict, df)
    return send_email(html_str)
