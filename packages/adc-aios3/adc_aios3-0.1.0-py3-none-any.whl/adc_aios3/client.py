"""S3 client implementation."""

import contextlib
from http import HTTPStatus
from logging import getLogger
from typing import Union, IO, AsyncGenerator, Self, Dict, Optional
from uuid import uuid4

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

logger = getLogger(__name__)


class S3Client:
    """Async S3 client with lifecycle management.

    This client provides a clean interface for working with S3-compatible storage services.
    It handles connection lifecycle, provides methods for common operations, and includes
    error handling and connection management.

    Args:
        bucket: Default bucket name
        url: S3 endpoint URL
        access_key: Access key for authentication
        secret_key: Secret key for authentication
        **kwargs: Additional arguments passed to aiobotocore client
    """

    def __init__(
        self,
        bucket: str,
        url: str,
        access_key: str,
        secret_key: str,
        **kwargs
    ):
        self.session = get_session()
        self.url = url
        self.client: Optional[AioBaseClient] = None
        self._bucket_name = bucket
        self._access_key = access_key
        self._secret_key = secret_key
        self._kwargs = kwargs

        self._exit_stack = contextlib.AsyncExitStack()
        self.started = False

    @classmethod
    async def create(
        cls,
        bucket: str,
        url: str,
        access_key: str,
        secret_key: str,
        **kwargs
    ) -> Self:
        """Create and start a new S3 client instance.

        Args:
            bucket: Default bucket name
            url: S3 endpoint URL
            access_key: Access key for authentication
            secret_key: Secret key for authentication
            **kwargs: Additional arguments passed to aiobotocore client

        Returns:
            Started S3Client instance
        """
        inst = cls(bucket, url, access_key, secret_key, **kwargs)
        await inst.start()
        return inst

    async def start(self) -> None:
        """Start the S3 client and establish connection."""
        if self.started:
            logger.warning('Client already started')
            return

        self.client = await self._exit_stack.enter_async_context(
            self.session.create_client(
                's3',
                endpoint_url=self.url,
                aws_secret_access_key=self._access_key,
                aws_access_key_id=self._secret_key,
                **self._kwargs,
            )
        )
        self.started = True

    async def close(self) -> None:
        """Close the S3 client and cleanup resources."""
        if not (self.client and self.started):
            logger.warning('Client is not started')
            return
        await self._exit_stack.aclose()

    async def upload(
        self,
        file: Union[bytes, IO],
        key: Optional[str] = None,
        bucket: Optional[str] = None
    ) -> str:
        """Upload a file to S3.

        Args:
            file: File content as bytes or file-like object
            key: Object key (optional, will generate UUID if not provided)
            bucket: Bucket name (optional, uses default if not provided)

        Returns:
            Object key
        """
        bucket = bucket or self._bucket_name
        key = key or str(uuid4())
        await self.client.put_object(Bucket=bucket, Key=key, Body=file)
        return key

    async def download_chunks(
        self,
        key: str,
        bucket: Optional[str] = None,
        chunk_size: int = 1024
    ) -> AsyncGenerator[bytes, None]:
        """Download a file from S3 in chunks.

        Args:
            key: Object key
            bucket: Bucket name (optional, uses default if not provided)
            chunk_size: Size of chunks to yield

        Yields:
            File chunks as bytes
        """
        bucket = bucket or self._bucket_name
        response = await self.client.get_object(Bucket=bucket, Key=key)
        while True:
            data = await response['Body'].read(chunk_size)
            if not data:
                break
            yield data

    async def download(
        self,
        key: str,
        bucket: Optional[str] = None
    ) -> bytes:
        """Download a file from S3.

        Args:
            key: Object key
            bucket: Bucket name (optional, uses default if not provided)

        Returns:
            File content as bytes
        """
        bucket = bucket or self._bucket_name
        data = b''
        async for chunk in self.download_chunks(key, bucket=bucket):
            data += chunk
        return data

    async def delete(
        self,
        key: str,
        bucket: Optional[str] = None
    ) -> None:
        """Delete an object from S3.

        Args:
            key: Object key
            bucket: Bucket name (optional, uses default if not provided)
        """
        bucket = bucket or self._bucket_name
        return await self.client.delete_object(Bucket=bucket, Key=key)

    async def generate_upload_url(
        self,
        key: str,
        expiration: int = 3600,
        bucket: Optional[str] = None
    ) -> str:
        """Generate a presigned URL for uploading.

        Args:
            key: Object key
            expiration: URL expiration time in seconds
            bucket: Bucket name (optional, uses default if not provided)

        Returns:
            Presigned URL for uploading
        """
        bucket = bucket or self._bucket_name
        return await self.client.generate_presigned_post(
            Bucket=bucket,
            Key=key,
            ExpiresIn=expiration,
        )

    async def generate_download_url(
        self,
        key: str,
        expiration: int = 3600,
        bucket: Optional[str] = None
    ) -> str:
        """Generate a presigned URL for downloading.

        Args:
            key: Object key
            expiration: URL expiration time in seconds
            bucket: Bucket name (optional, uses default if not provided)

        Returns:
            Presigned URL for downloading
        """
        bucket = bucket or self._bucket_name
        return await self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=expiration,
        )

    async def upload_chunks(
        self,
        file: AsyncGenerator[bytes, None],
        key: Optional[str] = None,
        bucket: Optional[str] = None
    ) -> str:
        """Upload a file to S3 in chunks.

        Args:
            file: Async generator yielding file chunks
            key: Object key (optional, will generate UUID if not provided)
            bucket: Bucket name (optional, uses default if not provided)

        Returns:
            Object key
        """
        bucket = bucket or self._bucket_name
        key = key or str(uuid4())

        response = await self.client.create_multipart_upload(Bucket=bucket, Key=key)
        upload_id = response['UploadId']

        parts = []
        part_number = 1

        try:
            async for chunk in file:
                part_response = await self.client.upload_part(
                    Bucket=bucket,
                    Key=key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk
                )

                parts.append({
                    'PartNumber': part_number,
                    'ETag': part_response['ETag']
                })

                part_number += 1

            await self.client.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
        except Exception:
            await self.client.abort_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id
            )
            raise

        return key

    async def get_metadata(
        self,
        key: str,
        bucket: Optional[str] = None
    ) -> Dict[str, str]:
        """Get object metadata.

        Args:
            key: Object key
            bucket: Bucket name (optional, uses default if not provided)

        Returns:
            Object metadata
        """
        bucket = bucket or self._bucket_name
        return await self.client.head_object(Bucket=bucket, Key=key)

    async def check_exist(
        self,
        key: str,
        bucket: Optional[str] = None
    ) -> bool:
        """Check if object exists.

        Args:
            key: Object key
            bucket: Bucket name (optional, uses default if not provided)

        Returns:
            True if object exists, False otherwise
        """
        try:
            meta = await self.get_metadata(key=key, bucket=bucket)
            return bool(meta)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    async def check_connection(self) -> bool:
        """Check if connection is established with S3.

        Returns:
            True if connection is established, False otherwise
        """
        try:
            resp = await self.client.list_buckets()
            return resp.get('ResponseMetadata', {}).get('HTTPStatusCode') == HTTPStatus.OK
        except Exception as exc:
            logger.error(exc)
        return False 