import boto3
from botocore.exceptions import ClientError

#  Assumes DynamoDB table named 'items' with 'id' as primary key

class DynamoDBHandler:
    def __init__(self, region_name='us-east-1'):  # Replace with your desired region
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table('items')

    def create_item(self, item_id, item_data):
        try:
            self.table.put_item(
                Item={
                    'id': item_id,
                    'data': item_data
                }
            )
            return True, None
        except ClientError as e:
            return False, e.response['Error']['Message']

    def get_item(self, item_id):
        try:
            response = self.table.get_item(
                Key={'id': item_id}
            )
            if 'Item' in response:
                return True, response['Item']
            else:
                return False, None  # Item not found
        except ClientError as e:
            return False, e.response['Error']['Message']

    def update_item(self, item_id, update_data):
        try:
            self.table.update_item(
                Key={'id': item_id},
                UpdateExpression='SET #d = :val',
                ExpressionAttributeNames={'#d': 'data'},
                ExpressionAttributeValues={':val': update_data}
            )
            return True, None
        except ClientError as e:
            return False, e.response['Error']['Message']

    def delete_item(self, item_id):
        try:
            self.table.delete_item(
                Key={'id': item_id}
            )
            return True, None
        except ClientError as e:
            return False, e.response['Error']['Message']