"""Contains the functionality to archive data that was recorded over a week ago into an S3 bucket."""
from os import environ, path, listdir, remove
import pandas as pd
from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from sqlalchemy import create_engine, URL

load_dotenv()


engine_url_object = URL.create(
        "postgresql+psycopg2",
        username=environ['DB_USER'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_HOST'],
        database=environ['DB_NAME'],
        )


def upload_file(s3_client: client, file: str, bucket: str, object_name=None):
    """Upload a file to an S3 bucket"""

    if object_name is None:
        object_name = path.basename(file)
    try:
        s3_client.upload_file(file, bucket, object_name)
    except ClientError as e:
        return False
    return True


def get_month_file(s3_client: client, date: datetime.date) -> pd.DataFrame:
    """Gets the s3 file that stores the monthly records, if available."""
    current_year = date.year
    current_month = date.month
    try:
        response = s3_client.get_object(Bucket="c9-tech-news", Key=f"{current_year}/{current_month}.csv")
    except ClientError as error:
        return "No such folder"
    return response



def data_manager() -> None:
    """Transfers records older than a week to an s3 bucket."""
    engine = create_engine(engine_url_object)
    date_cutoff = datetime.now() - timedelta(days=3)
    old_records = pd.read_sql(f"SELECT * FROM records WHERE record_time < '{date_cutoff}'", engine)
    old_records.to_csv("test_records.csv", index=False)
    
    s3 = client("s3",
                aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])



if __name__ == "__main__":

    s3 = client("s3",
                aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
                aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    print(get_month_file(s3, datetime.now()))
    # load_dotenv()
    # conn = get_db_connection()
    # s3 = client("s3",
    # aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
    # aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])

    # with conn:
    #     current_date = datetime.now().strftime('%Y-%m-%d')

    #     reading_data = pd.read_sql('SELECT * FROM stories;', conn)
    #     reading_data.to_csv(f"{current_date}_backup_stories.csv" ,index=False)
