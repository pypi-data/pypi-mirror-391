"""
AWS client factory with retry logic and configuration.

This module provides singleton boto3 clients with proper retry configuration
to avoid recreating clients on every Lambda invocation.
"""

import boto3
import os
from botocore.config import Config
from typing import Optional


# Singleton clients cache
_clients = {}


def get_boto3_config() -> Config:
    """
    Get standard boto3 configuration with retries.

    Returns:
        Configured botocore Config object

    Configuration includes:
    - Adaptive retry mode with max 3 attempts
    - 5 second connect timeout
    - 10 second read timeout
    """
    return Config(
        retries={
            'max_attempts': 3,
            'mode': 'adaptive'
        },
        connect_timeout=5,
        read_timeout=10,
        max_pool_connections=50
    )


def get_region() -> str:
    """
    Get AWS region from environment or default.

    Returns:
        AWS region name
    """
    return os.environ.get('AWS_REGION', 'us-east-1')


def get_dynamodb_client():
    """
    Get DynamoDB client with retries (low-level client).

    Returns:
        boto3 DynamoDB client

    Example:
        >>> client = get_dynamodb_client()
        >>> response = client.get_item(TableName='users', Key={'id': {'S': '123'}})
    """
    if 'dynamodb' not in _clients:
        _clients['dynamodb'] = boto3.client(
            'dynamodb',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['dynamodb']


def get_dynamodb_resource():
    """
    Get DynamoDB resource (high-level interface).

    Returns:
        boto3 DynamoDB resource

    Example:
        >>> dynamodb = get_dynamodb_resource()
        >>> table = dynamodb.Table('users')
        >>> response = table.get_item(Key={'id': '123'})
    """
    if 'dynamodb_resource' not in _clients:
        _clients['dynamodb_resource'] = boto3.resource(
            'dynamodb',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['dynamodb_resource']


def get_cognito_client():
    """
    Get Cognito Identity Provider client with retries.

    Returns:
        boto3 Cognito IDP client

    Example:
        >>> client = get_cognito_client()
        >>> response = client.admin_get_user(UserPoolId='...', Username='...')
    """
    if 'cognito' not in _clients:
        _clients['cognito'] = boto3.client(
            'cognito-idp',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['cognito']


def get_s3_client():
    """
    Get S3 client with retries.

    Returns:
        boto3 S3 client

    Example:
        >>> client = get_s3_client()
        >>> response = client.get_object(Bucket='my-bucket', Key='file.txt')
    """
    if 's3' not in _clients:
        _clients['s3'] = boto3.client(
            's3',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['s3']


def get_ses_client():
    """
    Get SES (Simple Email Service) client with retries.

    Returns:
        boto3 SES client

    Example:
        >>> client = get_ses_client()
        >>> response = client.send_email(Source='...', Destination={...}, Message={...})
    """
    if 'ses' not in _clients:
        _clients['ses'] = boto3.client(
            'ses',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['ses']


def get_sns_client():
    """
    Get SNS (Simple Notification Service) client with retries.

    Returns:
        boto3 SNS client

    Example:
        >>> client = get_sns_client()
        >>> response = client.publish(TopicArn='...', Message='...')
    """
    if 'sns' not in _clients:
        _clients['sns'] = boto3.client(
            'sns',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['sns']


def get_lambda_client():
    """
    Get Lambda client with retries (for inter-service invocation).

    Returns:
        boto3 Lambda client

    Example:
        >>> client = get_lambda_client()
        >>> response = client.invoke(FunctionName='...', Payload='...')
    """
    if 'lambda' not in _clients:
        _clients['lambda'] = boto3.client(
            'lambda',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['lambda']


def get_secrets_client():
    """
    Get Secrets Manager client with retries.

    Returns:
        boto3 Secrets Manager client

    Example:
        >>> client = get_secrets_client()
        >>> response = client.get_secret_value(SecretId='my-secret')
    """
    if 'secrets' not in _clients:
        _clients['secrets'] = boto3.client(
            'secretsmanager',
            region_name=get_region(),
            config=get_boto3_config()
        )
    return _clients['secrets']


def clear_clients():
    """
    Clear all cached clients.

    Useful for testing or when clients need to be refreshed.
    """
    global _clients
    _clients = {}
