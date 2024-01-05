from os import environ
from dotenv import load_dotenv
import pandas as pd
import boto3
from datetime import date
import psycopg2
from openai import OpenAI
import json


def get_db_connection():
    '''Forms AWS RDS postgres connection.'''
    try:
        conn = psycopg2.connect(dbname=environ["DB_NAME"],
                                host=environ["DB_HOST"],
                                user=environ["DB_USER"],
                                password=environ["DB_PASSWORD"],
                                port=environ["DB_PORT"])
        return conn
    except Exception as e:
        print(f'Error: Unable to form connection {e}')


def load_data():
    conn = get_db_connection()
    with conn.cursor() as curr:

        # choose stories with top 5 scores, but don't allow repeats
        curr.execute("""
                    SELECT DISTINCT ON (records.story_id) 
                     records.*, stories.* FROM records
                    JOIN stories ON records.story_id = stories.story_id 
                    WHERE record_time >= NOW() - INTERVAL '24 HOURS'
                    ORDER BY records.story_id, records.score DESC LIMIT 5;
                     ;
                    """)
        data = curr.fetchall()
        df = pd.DataFrame(data)
        column_names = [desc[0] for desc in curr.description]
        df.columns = column_names
        curr.close()
    return df


def get_url_list():
    df = load_data()
    return df['story_url'].to_list()


def summarise_story(url_list:list[str]):
    '''Uses OpenAI lambda function to generate .'''

    client = OpenAI(api_key=environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a newsletter writer, producing a newsletter similar to the morning brew."},
            {"role": "user", "content": f"""Write a summary approximately 200 words in length, that gives key insights for articles in list: {url_list}, 
                                            return a list of dictionaries with keys 'article_title' which includes the name of the article and 'summary for each article'."""}
            ],
        temperature=1
    )
    article_summary = response.choices[0].message.content.strip()
    return article_summary

def send_email(html_string:str):
    '''Sends email newsletter using generated html string.'''
    today = date.today()
    today_date = today.strftime("%B %d")
    # email_html = generate_html_string(top_10_articles)
    client = boto3.client('ses', region_name='eu-west-2', aws_access_key_id=environ["ACCESS_KEY_ID"],
                          aws_secret_access_key=environ["SECRET_ACCESS_KEY"])

    response = client.send_email(
        Destination={
            'ToAddresses': ['trainee.anurag.kaur@sigmalabs.co.uk']
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
                'Data': f'Daily Brief {today_date}',
            },
        },
        Source='trainee.anurag.kaur@sigmalabs.co.uk'
    )

    return response

def generate_html_string() -> str:
    '''Generates HTML string for the email.'''
    url_list = get_url_list()
    summary = summarise_story(url_list)
    dict_of_summary = json.loads(f"{summary}")
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
    for article in dict_of_summary:
        title = article.get('article_title')
        summary = article.get('summary')
        article_box = f"""<body style="border-width:3px; border-style:solid; border-color:#E6E6FA; border-radius: 12px; padding: 20px; border-spacing: 10px 2em;">
        <h2 style="color: #008B8B;"> {title}</h2>
        <p style="color:#6495ED"> {summary} </p> </body>"""
        articles_list.append(article_box)
    articles_string = " ".join(articles_list)
    html_full = html_start + articles_string + html_end
    return html_full

def handler(event=None, context=None):
    load_dotenv()
    html_str = generate_html_string()
    return send_email(html_str)


