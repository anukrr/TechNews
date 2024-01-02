'''Sends SMS if viral article detected. '''
from os import environ
from dotenv import load_dotenv
import pandas as pd
import psycopg2
import boto3

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

def check_viral_article():
    '''Checks for viral articles.'''
    pass

def send_email(article_title:str):
    '''Sends an SMS if viral article is detected.'''
    try:
        client = boto3.client('ses', region_name='eu-west-2', aws_access_key_id=environ["ACCESS_KEY_ID"],
                            aws_secret_access_key=environ["SECRET_ACCESS_KEY"])
        response = client.publish(
            PhoneNumber=environ["PHONE_NUMBER"],
            Message=f"Article '{article_title}' is gaining traction",
            Subject='string',
            MessageAttributes={
                'string': {
                    'DataType': 'String',
                }
            },
            MessageGroupId='string'
        )
        return response
    except Exception as e:
        print(f'Error sending SMS: {e}')

