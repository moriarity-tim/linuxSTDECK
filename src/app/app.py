from flask import Flask, request, jsonify
from dynamodb_handler import DynamoDBHandler
from s3_handler import S3Handler

app = Flask(__name__)
dynamodb_handler = DynamoDBHandler()
s3_handler = S3Handler()

@app.route('/items', methods=['POST'])
def create_item():
    item_id = request.json.get('id')
    item_data = request.json.get('data')

    if not item_id or not item_data:
        return jsonify({'error': 'Missing id or data in request body'}), 400

    success_db, error_db = dynamodb_handler.create_item(item_id, item_data)
    if not success_db:
        if "ConditionalCheckFailedException" in error_db: # or similar for duplicate
             return jsonify({'error': 'Item with this ID already exists'}), 409
        return jsonify({'error': f'DynamoDB Error: {error_db}'}), 500

    success_s3, error_s3 = s3_handler.upload_object(item_id, str(item_data))
    if not success_s3:
        # Rollback DynamoDB if S3 fails
        dynamodb_handler.delete_item(item_id)
        return jsonify({'error': f'S3 Error: {error_s3}'}), 500

    return jsonify({'message': 'Item created successfully'}), 201

@app.route('/items/<string:item_id>', methods=['GET'])
def get_item(item_id):
    success_db, item_data = dynamodb_handler.get_item(item_id)
    if not success_db:
        return jsonify({'error': f'DynamoDB Error: {item_data}'}), 500
    if not item_data:
        return jsonify({'message': 'Item not found'}), 404

    success_s3, s3_data = s3_handler.get_object(item_id)
    if not success_s3:
        return jsonify({'error': f'S3 Error: {s3_data}'}), 500
    
    return jsonify({'id': item_id, 'data': item_data['data'], 's3_data': s3_data}), 200

@app.route('/items/<string:item_id>', methods=['PUT'])
def update_item(item_id):
    update_data = request.json.get('data')

    if not update_data:
        return jsonify({'error': 'Missing data in request body'}), 400

    success_db, error_db = dynamodb_handler.update_item(item_id, update_data)
    if not success_db:
        return jsonify({'error': f'DynamoDB Error: {error_db}'}), 500

    success_s3, error_s3 = s3_handler.upload_object(item_id, str(update_data))
    if not success_s3:
        return jsonify({'error': f'S3 Error: {error_s3}'}), 500
    
    return jsonify({'message': 'Item updated successfully'}), 200

@app.route('/items/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    success_db, error_db = dynamodb_handler.delete_item(item_id)
    if not success_db:
        return jsonify({'error': f'DynamoDB Error: {error_db}'}), 500

    success_s3, error_s3 = s3_handler.delete_object(item_id)
    if not success_s3:
        return jsonify({'error': f'S3 Error: {error_s3}'}), 500

    return jsonify({'message': 'Item deleted successfully'}), 204

if __name__ == '__main__':
    app.run(debug=True)