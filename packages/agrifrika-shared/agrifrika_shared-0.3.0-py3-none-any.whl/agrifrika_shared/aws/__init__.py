"""
AWS client wrappers with retry logic.
"""

from .clients import (
    get_boto3_config,
    get_region,
    get_dynamodb_client,
    get_dynamodb_resource,
    get_cognito_client,
    get_s3_client,
    get_ses_client,
    get_sns_client,
    get_lambda_client,
    get_secrets_client,
    clear_clients,
)

from .dynamo_client import DynamoDBClient
from .cognito_client import CognitoClient

__all__ = [
    # Client factory
    "get_boto3_config",
    "get_region",
    "get_dynamodb_client",
    "get_dynamodb_resource",
    "get_cognito_client",
    "get_s3_client",
    "get_ses_client",
    "get_sns_client",
    "get_lambda_client",
    "get_secrets_client",
    "clear_clients",
    # Client wrappers
    "DynamoDBClient",
    "CognitoClient",
]
