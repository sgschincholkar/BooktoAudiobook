import os
import boto3
from botocore.exceptions import ClientError

# Module-level singleton — initialized once on first use
_r2_client = None


def get_r2_client():
    """Get boto3 S3 client configured for Cloudflare R2 (singleton)."""
    global _r2_client
    if _r2_client is not None:
        return _r2_client

    account_id = os.getenv("R2_ACCOUNT_ID")
    access_key_id = os.getenv("R2_ACCESS_KEY_ID")
    secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")

    if not all([account_id, access_key_id, secret_access_key]):
        raise ValueError("Missing R2 credentials in environment variables")

    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    _r2_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name="auto"
    )
    return _r2_client


def get_bucket_name() -> str:
    """Get R2 bucket name from environment."""
    bucket_name = os.getenv("R2_BUCKET_NAME")
    if not bucket_name:
        raise ValueError("R2_BUCKET_NAME environment variable not set")
    return bucket_name


def upload_file(key: str, data: bytes) -> str:
    """
    Upload file to Cloudflare R2.

    Args:
        key: Object key (file path in bucket)
        data: File contents as bytes

    Returns:
        The object key

    Raises:
        Exception: If upload fails
    """
    try:
        client = get_r2_client()
        bucket = get_bucket_name()

        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data
        )

        return key

    except ClientError as e:
        raise Exception(f"R2 upload failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Storage error: {str(e)}")


def download_file(key: str) -> bytes:
    """
    Download file from Cloudflare R2.

    Args:
        key: Object key (file path in bucket)

    Returns:
        File contents as bytes

    Raises:
        Exception: If download fails
    """
    try:
        client = get_r2_client()
        bucket = get_bucket_name()

        response = client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()

    except ClientError as e:
        raise Exception(f"R2 download failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Storage error: {str(e)}")


def generate_presigned_url(key: str, expiration: int = 3600) -> str:
    """
    Generate a presigned URL for downloading a file.

    Args:
        key: Object key (file path in bucket)
        expiration: URL expiration time in seconds (default 1 hour)

    Returns:
        Presigned URL string

    Raises:
        Exception: If URL generation fails
    """
    try:
        client = get_r2_client()
        bucket = get_bucket_name()

        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expiration
        )

        return url

    except ClientError as e:
        raise Exception(f"Presigned URL generation failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Storage error: {str(e)}")
