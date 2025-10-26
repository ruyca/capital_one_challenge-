import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def get_s3_client():
    """
    Create and return an S3 client with credentials from environment variables.
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        return s3_client
    except Exception as e:
        print(f"Error creating S3 client: {str(e)}")
        raise


def upload_html_to_s3(html_content: str, company_name: str, metadata: dict = None, url_expiration_days: int = 7) -> dict:
    """
    Upload HTML content to S3 and return a pre-signed URL.
    
    Args:
        html_content: The HTML content to upload
        company_name: Name of the company (used for filename)
        metadata: Optional dictionary with additional metadata
        url_expiration_days: Number of days before the URL expires (default: 7)
    
    Returns:
        Dictionary containing the S3 key, pre-signed URL, and bucket info
    """
    try:
        # Validate that bucket name is set
        if not S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME not set in environment variables")
        
        # Create S3 client
        s3_client = get_s3_client()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company_name = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '_').lower()
        s3_key = f"brand-websites/{safe_company_name}_{timestamp}.html"
        
        # Prepare metadata for S3
        s3_metadata = {
            'company-name': company_name,
            'upload-timestamp': timestamp,
            'content-type': 'text/html'
        }
        
        # Add additional metadata if provided
        if metadata:
            for key, value in metadata.items():
                # S3 metadata keys must be lowercase and cannot have special characters
                safe_key = key.lower().replace('_', '-')
                s3_metadata[safe_key] = str(value)
        
        # Upload to S3 without ACL (bucket policy handles public access)
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=html_content.encode('utf-8'),
            ContentType='text/html',
            Metadata=s3_metadata
            # ACL removed - use bucket policy instead for public access
        )
        
        # Calculate expiration in seconds
        expiration_seconds = url_expiration_days * 24 * 60 * 60
        
        # Generate a pre-signed URL
        public_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': s3_key,
                'ResponseContentDisposition': 'inline'
            },
            ExpiresIn=expiration_seconds
        )
        
        print(f"✅ Successfully uploaded to S3: {s3_key}")
        print(f"🌐 Pre-signed URL (expires in {url_expiration_days} days): {public_url}")
        
        return {
            "success": True,
            "s3_key": s3_key,
            "bucket": S3_BUCKET_NAME,
            "region": AWS_REGION,
            "public_url": public_url,
            "url_expires_in": "7 days",
            "timestamp": timestamp
        }
        
    except NoCredentialsError:
        error_msg = "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"❌ S3 ClientError ({error_code}): {error_msg}")
        raise Exception(f"S3 upload failed: {error_msg}")
    
    except Exception as e:
        print(f"❌ Unexpected error uploading to S3: {str(e)}")
        raise


def check_s3_configuration() -> dict:
    """
    Check if S3 is properly configured and accessible.
    
    Returns:
        Dictionary with configuration status
    """
    config_status = {
        "aws_access_key_set": bool(AWS_ACCESS_KEY_ID),
        "aws_secret_key_set": bool(AWS_SECRET_ACCESS_KEY),
        "bucket_name_set": bool(S3_BUCKET_NAME),
        "region": AWS_REGION,
        "bucket_accessible": False
    }
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
        return config_status
    
    try:
        s3_client = get_s3_client()
        # Try to head the bucket to check if it's accessible
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        config_status["bucket_accessible"] = True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"Bucket check failed with error: {error_code}")
        config_status["bucket_accessible"] = False
    except Exception as e:
        print(f"Error checking S3 configuration: {str(e)}")
        config_status["bucket_accessible"] = False
    
    return config_status


def list_uploaded_files(prefix: str = "brand-websites/", max_items: int = 100) -> list:
    """
    List files uploaded to S3 under a specific prefix.
    
    Args:
        prefix: The S3 prefix (folder path) to search
        max_items: Maximum number of items to return
    
    Returns:
        List of dictionaries containing file information
    """
    try:
        if not S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME not set in environment variables")
        
        s3_client = get_s3_client()
        
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_items
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                # Generate pre-signed URL for each file (expires in 7 days)
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': S3_BUCKET_NAME,
                        'Key': obj['Key'],
                        'ResponseContentDisposition': 'inline'
                    },
                    ExpiresIn=604800  # 7 days
                )
                
                file_info = {
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': presigned_url,
                    'url_expires_in': '7 days'
                }
                files.append(file_info)
        
        return files
        
    except Exception as e:
        print(f"Error listing S3 files: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    # Check configuration
    status = check_s3_configuration()
    print("S3 Configuration Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test upload (uncomment to test)
    # test_html = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test Upload</h1></body></html>"
    # result = upload_html_to_s3(test_html, "test_company", {"tone": "formal", "style": "modern"})
    # print(f"\nUpload Result: {result}")
