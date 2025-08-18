import unittest
from app import app, dynamodb_handler, s3_handler
import json

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Clear DynamoDB and S3 for a clean test environment (handle with care in production)
        # You'll need to implement actual cleanup methods in your handlers if desired
        # For simplicity here, we assume a clean state before each test.

    def test_post_item_success(self):
        item_id = 'test_post_item_1'
        item_data = {'name': 'Test Item 1', 'description': 'This is a test item'}
        response = self.app.post('/items', json={'id': item_id, 'data': item_data})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Item created successfully', response.json['message'])

        # Verify DynamoDB and S3
        success_db, db_item = dynamodb_handler.get_item(item_id)
        self.assertTrue(success_db)
        self.assertEqual(db_item['data'], item_data)

        success_s3, s3_object = s3_handler.get_object(item_id)
        self.assertTrue(success_s3)
        self.assertEqual(json.loads(s3_object), item_data)

    def test_post_item_duplicate(self):
        item_id = 'test_post_item_duplicate'
        item_data = {'name': 'Duplicate Item', 'description': 'Testing duplicate'}
        self.app.post('/items', json={'id': item_id, 'data': item_data}) # First post

        response = self.app.post('/items', json={'id': item_id, 'data': item_data}) # Duplicate post
        self.assertEqual(response.status_code, 409)
        self.assertIn('Item with this ID already exists', response.json['error'])

    def test_get_item_success(self):
        item_id = 'test_get_item_1'
        item_data = {'name': 'Get Test Item', 'category': 'Test'}
        dynamodb_handler.create_item(item_id, item_data)
        s3_handler.upload_object(item_id, json.dumps(item_data))

        response = self.app.get(f'/items/{item_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['id'], item_id)
        self.assertEqual(response.json['data'], item_data)
        self.assertEqual(json.loads(response.json['s3_data']), item_data)

    def test_get_item_not_found(self):
        response = self.app.get('/items/non_existent_item')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Item not found', response.json['message'])

    def test_put_item_success(self):
        item_id = 'test_put_item_1'
        initial_data = {'name': 'Initial', 'status': 'Pending'}
        updated_data = {'name': 'Updated', 'status': 'Completed'}
        dynamodb_handler.create_item(item_id, initial_data)
        s3_handler.upload_object(item_id, json.dumps(initial_data))

        response = self.app.put(f'/items/{item_id}', json={'data': updated_data})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Item updated successfully', response.json['message'])

        # Verify DynamoDB and S3
        success_db, db_item = dynamodb_handler.get_item(item_id)
        self.assertTrue(success_db)
        self.assertEqual(db_item['data'], updated_data)

        success_s3, s3_object = s3_handler.get_object(item_id)
        self.assertTrue(success_s3)
        self.assertEqual(json.loads(s3_object), updated_data)

    def test_delete_item_success(self):
        item_id = 'test_delete_item_1'
        item_data = {'name': 'Delete Me'}
        dynamodb_handler.create_item(item_id, item_data)
        s3_handler.upload_object(item_id, json.dumps(item_data))

        response = self.app.delete(f'/items/{item_id}')
        self.assertEqual(response.status_code, 204)

        # Verify DynamoDB and S3
        success_db, db_item = dynamodb_handler.get_item(item_id)
        self.assertFalse(success_db) # Item should be deleted
        self.assertIsNone(db_item)

        success_s3, s3_object = s3_handler.get_object(item_id)
        self.assertFalse(success_s3) # Object should be deleted
        self.assertIsNone(s3_object)

    def test_delete_item_not_found(self):
        response = self.app.delete('/items/non_existent_item_delete')
        self.assertEqual(response.status_code, 204) # Or 404 depending on your desired API behavior

if __name__ == '__main__':
    unittest.main()