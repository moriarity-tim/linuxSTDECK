import unittest
import json
from unittest.mock import MagicMock
from app import app, dynamodb, s3, DYNAMODB_TABLE_NAME, S3_BUCKET_NAME

class TestAPI(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

        # Mock Boto3 interactions for DynamoDB and S3
        dynamodb.put_item = MagicMock()
        dynamodb.get_item = MagicMock()
        dynamodb.update_item = MagicMock()
        dynamodb.delete_item = MagicMock()

        s3.put_object = MagicMock()
        s3.get_object = MagicMock()
        s3.delete_object = MagicMock()

    def test_create_item(self):
        item_data = {"id": "123", "name": "Test Item"}
        response = self.app.post('/items', json=item_data)
        self.assertEqual(response.status_code, 201)
        dynamodb.put_item.assert_called_once()
        s3.put_object.assert_called_once()

    def test_get_item(self):
        # Configure mock responses for DynamoDB and S3
        dynamodb.get_item.return_value = {
            'Item': {'id': {'S': '123'}, 'name': {'S': 'Test Item'}}
        }
        s3.get_object.return_value = {
            'Body': MagicMock(read=lambda: json.dumps({"id": "123", "name": "Test Item"}).encode('utf-8'))
        }

        response = self.app.get('/items/123')
        self.assertEqual(response.status_code, 200)
        dynamodb.get_item.assert_called_once()
        s3.get_object.assert_called_once()

    def test_update_item(self):
        updated_data = {"name": "Updated Item Name"}
        response = self.app.put('/items/123', json=updated_data)
        self.assertEqual(response.status_code, 200)
        dynamodb.update_item.assert_called_once()
        s3.put_object.assert_called_once()

    def test_delete_item(self):
        response = self.app.delete('/items/123')
        self.assertEqual(response.status_code, 204)
        dynamodb.delete_item.assert_called_once()
        s3.delete_object.assert_called_once()

if __name__ == '__main__':
    unittest.main()