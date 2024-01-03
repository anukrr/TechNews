from os import environ
from dotenv import load_dotenv
import pandas as pd
import boto3
from datetime import date
import psycopg2

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

def send_email(top_10_articles: list[dict]):
    today = date.today()
    date = today.strftime("%B %d")
    email_html = generate_html_string(top_10_articles)
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
                    'Data': email_html
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': f'Daily Brief {date}',
            },
        },
        Source='trainee.anurag.kaur@sigmalabs.co.uk'
    )

    return response

def generate_html_string(plants: list[dict]) -> str:
    """Generates HTML string for the email"""
    today = date.today()
    warning_string = '<body>'

    for plant in plants:

        plant_id = plant.get('plant_id')
        temperature = plant.get('temperature')
        avg = plant.get('avg_temp')
        if temperature > avg:
            difference = temperature - avg
            warning_string += f""" <li> Plant {plant_id} is above optimum temperature by {difference}˚C. The average temperature is {avg}˚C but the temperature is {temperature}˚C </li>"""

        if temperature < avg:
            difference = avg - temperature
            warning_string += f""" <li> Plant {plant_id} is below optimum temperature by {difference}˚C. The average temperature is {avg}˚C but the temperature is {temperature}˚C</li>"""

    warning_string += '</body>'
    return warning_string

# def handler(event=None, context=None):
#     load_dotenv()
#     connection = get_db_connection()
#     df = load_all_data(connection)
#     unhealthy_plants = check_plant_vitals(df)
#     if unhealthy_plants != []:
#         return send_email(unhealthy_plants)
#     return None
