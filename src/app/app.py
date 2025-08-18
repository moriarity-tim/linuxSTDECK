from flask import Flask, request, jsonify
import boto3
import os

app = Flask(__name__)


# Initialize DynamoDB and S3 clients
dynamodb = boto3.client('dynamodb', region_name=os.getenv('AWS_REGION'))
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION'))

DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

@app.route('/items', methods=['POST'])
def create_item():
    item_data = request.get_json()  # Accepts JSON data

    # Store in DynamoDB
    try:
        dynamodb.put_item(
            TableName=DYNAMODB_TABLE_NAME,
            Item={
                'id': {'S': item_data['id']}, # Assuming 'id' is your partition key
                'name': {'S': item_data['name']},
                # ... other attributes
            }
        )
        print(f"Item stored in DynamoDB: {item_data['id']}")
    except Exception as e:
        return jsonify({"error": f"DynamoDB error: {str(e)}"}), 500

    # Store in S3
    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"items/{item_data['id']}.json",
            Body=json.dumps(item_data),  # Convert JSON to string for S3
            ContentType='application/json'
        )
        print(f"Item stored in S3: items/{item_data['id']}.json")
    except Exception as e:
        return jsonify({"error": f"S3 error: {str(e)}"}), 500

    return jsonify({"message": "Item created successfully"}), 201

@app.route('/items/<string:item_id>', methods=['GET'])
def get_item(item_id):
    # Retrieve from DynamoDB
    try:
        response = dynamodb.get_item(
            TableName=DYNAMODB_TABLE_NAME,
            Key={'id': {'S': item_id}}
        )
        dynamodb_item = response.get('Item')
        if not dynamodb_item:
            return jsonify({"message": "Item not found in DynamoDB"}), 404
        # Convert DynamoDB item format to standard JSON
        item_from_dynamodb = {k: v[list(v.keys())[0]] for k, v in dynamodb_item.items()}
    except Exception as e:
        return jsonify({"error": f"DynamoDB error: {str(e)}"}), 500

    # Retrieve from S3
    try:
        response = s3.get_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"items/{item_id}.json"
        )
        s3_object_body = response['Body'].read().decode('utf-8')
        item_from_s3 = json.loads(s3_object_body)
    except Exception as e:
        return jsonify({"error": f"S3 error: {str(e)}"}), 500

    return jsonify({"dynamodb_item": item_from_dynamodb, "s3_item": item_from_s3}), 200

@app.route('/items/<string:item_id>', methods=['PUT'])
def update_item(item_id):
    updated_data = request.get_json()

    # Update in DynamoDB
    try:
        # Build UpdateExpression based on the data
        update_expression = "SET "
        expression_attribute_values = {}
        for key, value in updated_data.items():
            if key != 'id':  # Prevent updating the primary key
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f':{key}'] = {'S': value} # Assuming string type

        update_expression = update_expression.rstrip(', ') # Remove trailing comma

        dynamodb.update_item(
            TableName=DYNAMODB_TABLE_NAME,
            Key={'id': {'S': item_id}},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        print(f"Item updated in DynamoDB: {item_id}")
    except Exception as e:
        return jsonify({"error": f"DynamoDB error: {str(e)}"}), 500

    # Update in S3 (overwriting the existing object)
    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"items/{item_id}.json",
            Body=json.dumps(updated_data),
            ContentType='application/json'
        )
        print(f"Item updated in S3: items/{item_id}.json")
    except Exception as e:
        return jsonify({"error": f"S3 error: {str(e)}"}), 500

    return jsonify({"message": "Item updated successfully"}), 200

@app.route('/items/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    # Delete from DynamoDB
    try:
        dynamodb.delete_item(
            TableName=DYNAMODB_TABLE_NAME,
            Key={'id': {'S': item_id}}
        )
        print(f"Item deleted from DynamoDB: {item_id}")
    except Exception as e:
        return jsonify({"error": f"DynamoDB error: {str(e)}"}), 500

    # Delete from S3
    try:
        s3.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"items/{item_id}.json"
        )
        print(f"Item deleted from S3: items/{item_id}.json")
    except Exception as e:
        return jsonify({"error": f"S3 error: {str(e)}"}), 500

    return jsonify({"message": "Item deleted successfully"}), 204


if __name__ == '__main__':
    app.run(debug=True)