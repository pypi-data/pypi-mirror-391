"""Tests for S3Client."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aios3 import S3Client


@pytest.fixture
def mock_session():
    """Create a mock session."""
    with patch('aios3.client.get_session') as mock:
        session = MagicMock()
        mock.return_value = session
        yield session


@pytest.fixture
def mock_client():
    """Create a mock S3 client."""
    client = AsyncMock()
    client.__aenter__.return_value = client
    return client


@pytest.fixture
async def s3_client(mock_session, mock_client):
    """Create a test S3 client instance."""
    mock_session.create_client.return_value = mock_client
    client = await S3Client.create(
        bucket="test-bucket",
        url="http://localhost:9000",
        access_key="test-key",
        secret_key="test-secret"
    )
    return client


@pytest.mark.asyncio
async def test_client_creation(s3_client):
    """Test client creation and initialization."""
    assert s3_client.started
    assert s3_client.client is not None


@pytest.mark.asyncio
async def test_upload(s3_client):
    """Test file upload."""
    test_data = b"test data"
    key = await s3_client.upload(test_data)
    s3_client.client.put_object.assert_called_once()
    assert key is not None


@pytest.mark.asyncio
async def test_download(s3_client):
    """Test file download."""
    test_data = b"test data"
    mock_response = {
        'Body': AsyncMock()
    }
    mock_response['Body'].read.side_effect = [test_data, b'']
    s3_client.client.get_object.return_value = mock_response

    data = await s3_client.download("test-key")
    assert data == test_data


@pytest.mark.asyncio
async def test_delete(s3_client):
    """Test file deletion."""
    await s3_client.delete("test-key")
    s3_client.client.delete_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="test-key"
    )


@pytest.mark.asyncio
async def test_generate_urls(s3_client):
    """Test URL generation."""
    # Test upload URL
    upload_url = await s3_client.generate_upload_url("test-key")
    s3_client.client.generate_presigned_post.assert_called_once()

    # Test download URL
    download_url = await s3_client.generate_download_url("test-key")
    s3_client.client.generate_presigned_url.assert_called_once()


@pytest.mark.asyncio
async def test_check_exist(s3_client):
    """Test existence check."""
    # Test existing object
    s3_client.client.head_object.return_value = {"ETag": "test"}
    assert await s3_client.check_exist("test-key")

    # Test non-existing object
    s3_client.client.head_object.side_effect = Exception("404")
    assert not await s3_client.check_exist("test-key")


@pytest.mark.asyncio
async def test_check_connection(s3_client):
    """Test connection check."""
    # Test successful connection
    s3_client.client.list_buckets.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }
    assert await s3_client.check_connection()

    # Test failed connection
    s3_client.client.list_buckets.side_effect = Exception("Connection error")
    assert not await s3_client.check_connection()


@pytest.mark.asyncio
async def test_close(s3_client):
    """Test client closure."""
    await s3_client.close()
    assert not s3_client.started 