import json

import boto3
from botocore.exceptions import ClientError

from ..config import settings
from ..constants import Secret
from ..logging import Logger

logger = Logger(__name__).logger


def get_secret():
    secret_name = Secret.OPENAI_API_KEY
    region_name = settings.REGION_NAME

    session = boto3.session.Session(region_name=region_name)
    client = session.client(service_name=Secret.SERVICE_NAME, region_name=region_name)

    try:
        logger.info(f"Getting secret value for {secret_name}")
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response["SecretString"]
        secret_dict = json.loads(secret)

        return secret_dict.get("OPENAI_API_KEY", None)
    except ClientError as e:
        logger.error(f"Failed to get secret value: {e}")


def get_openai_api_key():
    if settings.ENVIRONMENT.is_local:
        import os

        return os.getenv("OPENAI_API_KEY")
    elif settings.ENVIRONMENT.is_production:
        return get_secret()
    else:
        raise ValueError("Unknown environment %s" % settings.ENVIRONMENT)
