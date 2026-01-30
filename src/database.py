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

def get_database_url():
    """Build the database URL based on the app configurations"""
    settings = get_settings()

    logger.info(f"Building database URL for the environment: {settings.env}")

    if settings.env == "LOCAL":
        logger.info(f"Using Local Environment variables for database credentials")
        return f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    else:
        logger.info(f"Using AWS Secrets Manager for database credentials")
        creds = get_secret()
        return f"mysql+pymysql://{creds['username']}:{creds['password']}@{creds['host']}:{creds['port', 3306]}/{creds['dbname']}"

DATABASE_URL = get_database_url()

logger.info(f"Creating database engine")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=15,
    echo=False
)


# Create SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

logger.info("Database configuration complete")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()