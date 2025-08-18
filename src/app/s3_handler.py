import boto3
from botocore.exceptions import ClientError

#  Replace with your S3 bucket name
S3_BUCKET_NAME = 'your-unique-s3-bucket-name'

class S3Handler:
    def __init__(self, region_name='us-east-1'):
        self.s3 = boto3.client('s3', region_name=region_name)

    def upload_object(self, key, data):
        try:
            self.s3.put_object(Bucket=S3_BUCKET_NAME, Key=key, Body=data)
            return True, None
        except ClientError as e:
            return False, e.response['Error']['Message']

    def get_object(self, key):
        try:
            response = self.s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
            return True, response['Body'].read().decode('utf-8')  # Assuming data is text
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return False, None  # Object not found
            else:
                return False, e.response['Error']['Message']

    def delete_object(self, key):
        try:
            self.s3.delete_object(Bucket=S3_BUCKET_NAME, Key=key)
            return True, None
        except ClientError as e:
            return False, e.response['Error']['Message']