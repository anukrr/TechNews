"""Contains the functionality to archive week-old records to s3."""
from os import environ, path
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, URL, text

load_dotenv()

WEEK_DAY_COUNT = 7
BUCKET = "c9-tech-news"


engine_url_object = URL.create(
        "postgresql+psycopg2",
        username=environ["DB_USER"],
        password=environ["DB_PASSWORD"],
        host=environ["DB_HOST"],
        database=environ["DB_NAME"],
        )


def upload_file(s3_client: client, file: str, bucket: str, object_name=None):
    """Upload a file to an S3 bucket"""

    if object_name is None:
        object_name = path.basename(file)
    try:
        s3_client.upload_file(file, bucket, object_name)
    except ClientError:
        return False
    return True


def get_month_file(s3_client: client, date: datetime.date) -> pd.DataFrame:
    """Gets the s3 file that stores the monthly records, if available."""
    current_year = date.year
    current_month = date.month
    try:
        response = s3_client.get_object(Bucket=BUCKET,
                                        Key=f"{current_year}/{current_month}.csv").get("Body")
    except ClientError:
        return pd.DataFrame
    try:
        monthly_df = pd.read_csv(response)
        return monthly_df
    except pd.errors.EmptyDataError:
        return pd.DataFrame


def lambda_handler(event, context):
    """Transfers records older than a week to an s3 bucket & removes them from RDS."""
    today = datetime.today()
    engine = create_engine(engine_url_object)
    date_cutoff = datetime.now() - timedelta(days=WEEK_DAY_COUNT)
    old_records = pd.read_sql(f"SELECT * FROM records WHERE record_time < '{date_cutoff}';",
                               engine)

    s3 = client("s3",
                aws_access_key_id=environ["ACCESS_KEY_ID"],
                aws_secret_access_key=environ["SECRET_ACCESS_KEY"])
    month_df = get_month_file(s3, today)
    if month_df.empty is False:
        month_df = pd.concat([month_df, old_records], ignore_index=True)
    else:
        month_df = old_records

    file_key = f"{today.year}/{today.month}.csv"
    csv_body = month_df.to_csv(index=False)
    s3.put_object(Body=csv_body, Bucket=BUCKET, Key=file_key)

    with engine.connect() as conn:
        delete_query = text(f"DELETE FROM records WHERE record_time < '{date_cutoff}';")
        conn.execute(delete_query)

