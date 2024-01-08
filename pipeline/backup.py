from os import environ, path, listdir, remove
import pandas as pd
from psycopg2 import connect
from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import ClientError
from datetime import datetime


def get_db_connection():
    """Returns a database connection."""
    try:
        connection = connect(
            host=environ["DB_HOST"],
            port=environ["DB_PORT"],
            database=environ["DB_NAME"],
            user=environ["DB_USER"],
            password=environ["DB_PASSWORD"]
        )
        return connection
    except OSError:
        return {'error': 'Unable to connect to the database.'}
    
def upload_file(s3_client: client, file: str, bucket: str, object_name=None):
    """Upload a file to an S3 bucket"""
    

    if object_name is None:
        object_name = path.basename(file)

    try:
        s3_client.upload_file(file, bucket, object_name)
    except ClientError as e:
        return False
    return True


if __name__ == "__main__":
    load_dotenv()
    conn = get_db_connection()
    s3 = client("s3",
    aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])

    with conn:
        current_date = datetime.now().strftime('%Y-%m-%d')

        reading_data = pd.read_sql('SELECT * FROM stories;', conn)
        reading_data.to_csv(f"{current_date}_backup_stories.csv" ,index=False)
