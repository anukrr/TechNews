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
    finally:
        conn.close()

list_of_url=["https://cachemon.github.io/SIEVE-website/blog/2023/12/17/sieve-is-simpler-than-lru/",
"https://fixmyblinds.com/",
"https://www.oreilly.com/library/view/50-algorithms-every/9781803247762/",
"https://arxiv.org/abs/2312.17661",
"https://blog.cr.yp.to/20240102-hybrid.html"]

def summarise_story(url_list:list[str]):
    client = OpenAI(api_key=environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a newsletter writer."},
        {"role": "user", "content": f"Write a comprehensive 150 word summary for articles in this list {url_list}, return a list of dictionaries with keys 'article_title' and 'summary for each article'"}
        ],
        temperature=0.5
    )
    article_summary = response.choices[0].message.content.strip()
    return article_summary


def get_article_title(url: str):
    client = OpenAI(api_key=environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a newsletter writer."},
            {"role": "user", "content": f"Return title for the article at this {url}"}
        ],
        temperature=0.5
    )
    title = response.choices[0].message.content.strip()
    return title
def send_email(html_string:str):
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
    """Generates HTML string for the email"""
    summary = summarise_story(list_of_url)
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
        article_box = f"""<body style="border-width:3px; border-style:solid; border-color:#E6E6FA; border-radius: 12px; padding: 20px;">
        <h2 style="color: #008B8B;"> {title}</h2>
        <p style="color:#6495ED"> {summary} </p> </body>"""
        articles_list.append(article_box)
    articles_string = " ".join(articles_list)
    html_full = html_start + articles_string + html_end
    return html_full

# def handler(event=None, context=None):
#     load_dotenv()
#     connection = get_db_connection()
#     df = load_all_data(connection)
#     unhealthy_plants = check_plant_vitals(df)
#     if unhealthy_plants != []:
#         return send_email(unhealthy_plants)
#     return None
load_dotenv()

html_str=generate_html_string()
send_email(html_str)