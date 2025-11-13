# ADC-AioS3

ADC-AioS3 is a modern, async-first S3 client library for Python that provides a clean and intuitive interface for working with S3-compatible storage services.

## Features

- 🚀 Fully async/await based
- 🔄 Automatic lifecycle management
- 📦 Support for multipart uploads
- 🔗 Presigned URL generation
- 📝 Comprehensive metadata handling
- 🛡️ Error handling and connection management

## Installation

```bash
pip install adc-aios3
```

## Quick Start

```python
import asyncio
from adc_aios3 import S3Client

async def main():
    # Create and start the client
    client = await S3Client.create(
        bucket="my-bucket",
        url="http://localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin"
    )

    # Upload a file
    with open("example.txt", "rb") as f:
        key = await client.upload(f, "example.txt")

    # Download a file
    data = await client.download(key)
    
    # Generate a presigned URL
    url = await client.generate_download_url(key, expiration=3600)

    # Clean up
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

For more detailed documentation, visit [adc-aios3.readthedocs.io](https://adc-aios3.readthedocs.io/).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
