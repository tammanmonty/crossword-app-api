from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings
import boto3
import json
import logging

Base = declarative_base()

logger = logging.getLogger(__name__)

def get_secret():
    """ Retrieve the Secret Information for the AWS Database
        AWS specifics can be retrieved from the config settings script which in turn is defined by the .env file
    """
    settings = get_settings()

    session = boto3.session.Session()

    client = session.client(
        service_name='secretsmanager',
        region_name=settings.aws_region
    )

    try:

        get_secret_value_response = client.get_secret_value(
            SecretId=settings.secret_name
        )
        return json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        logger.error(f"Error with boto3 client {e}")

    except Exception as e:
        logger.error(f"Unexpected error with getting AWS Secrets {e}")