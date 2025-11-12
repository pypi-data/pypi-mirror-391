"""Pytest configuration and shared fixtures for agrifrika-shared tests."""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any
import json


@pytest.fixture
def mock_dynamodb_client():
    """Mock DynamoDB client for testing."""
    mock = Mock()
    mock.get_item.return_value = {"Item": {"id": "test-123", "name": "Test Item"}}
    mock.put_item.return_value = None
    mock.query.return_value = {
        "Items": [{"id": "1", "name": "Item 1"}],
        "Count": 1,
        "ScannedCount": 1
    }
    mock.scan.return_value = {
        "Items": [{"id": "1", "name": "Item 1"}],
        "Count": 1,
        "ScannedCount": 1
    }
    mock.update_item.return_value = {"Attributes": {"id": "test-123", "name": "Updated"}}
    mock.delete_item.return_value = None
    return mock


@pytest.fixture
def mock_cognito_client():
    """Mock Cognito client for testing."""
    mock = Mock()
    mock.admin_create_user.return_value = {
        "User": {
            "Username": "test-user",
            "Attributes": [
                {"Name": "email", "Value": "test@example.com"}
            ],
            "UserStatus": "FORCE_CHANGE_PASSWORD"
        }
    }
    mock.admin_set_user_password.return_value = None
    mock.admin_delete_user.return_value = None
    return mock


@pytest.fixture
def mock_lambda_client():
    """Mock Lambda client for testing."""
    mock = Mock()
    mock.invoke.return_value = {
        "StatusCode": 200,
        "Payload": Mock(read=lambda: json.dumps({"message": "Success"}).encode())
    }
    return mock


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing."""
    mock = Mock()
    mock.upload_file.return_value = None
    mock.download_file.return_value = None
    mock.put_object.return_value = None
    mock.get_object.return_value = {
        "Body": Mock(read=lambda: b"test data")
    }
    mock.delete_object.return_value = None
    return mock


@pytest.fixture
def sample_lambda_event() -> Dict[str, Any]:
    """Sample Lambda event for testing."""
    return {
        "httpMethod": "POST",
        "path": "/api/test",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token"
        },
        "body": json.dumps({"name": "Test", "value": 123}),
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "user-123",
                    "email": "test@example.com",
                    "cognito:username": "testuser"
                }
            },
            "requestId": "test-request-id"
        },
        "pathParameters": {"id": "test-123"},
        "queryStringParameters": {"limit": "10", "status": "active"},
        "isBase64Encoded": False
    }


@pytest.fixture
def sample_lambda_context():
    """Sample Lambda context for testing."""
    context = Mock()
    context.function_name = "test-function"
    context.function_version = "1"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    context.memory_limit_in_mb = 128
    context.aws_request_id = "test-request-id"
    context.log_group_name = "/aws/lambda/test-function"
    context.log_stream_name = "2024/01/01/[$LATEST]abcdef123456"
    return context


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.error = Mock()
    logger.warning = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture(autouse=True)
def reset_env_vars(monkeypatch):
    """Reset environment variables before each test."""
    # Set common test environment variables
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("STAGE", "test")
    monkeypatch.setenv("USER_POOL_ID", "us-east-1_test")
    monkeypatch.setenv("USER_POOL_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("NOTIFICATION_SERVICE_ARN", "arn:aws:lambda:us-east-1:123456789012:function:test-notification")
