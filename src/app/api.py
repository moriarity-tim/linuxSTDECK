from flask import jsonify, request
from src.app import create_app

app = create_app()

# Simple in-memory data store for demonstration
items = {}
next_id = 1

@app.route('/items', methods=['GET'])
def get_items():
    """
    Handles GET requests to retrieve all items.
    Returns: JSON response with all items and a 200 status code.
    """
    return jsonify(list(items.values())), 200.

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """
    Handles GET requests to retrieve a specific item by ID.
    Args:
        item_id: The ID of the item to retrieve.
    Returns:
        JSON response with the item and a 200 status code if found,
        or a JSON error message and a 404 status code if not found.
    """
    item = items.get(item_id)
    if item:
        return jsonify(item), 200
    return jsonify({'message': 'Item not found'}), 404.

@app.route('/items', methods=['POST'])
def create_item():
    """
    Handles POST requests to create a new item.
    Expects a JSON request body with 'name'.
    Returns:
        JSON response with the created item and a 201 status code if successful,
        or a JSON error message and a 400 status code if the request is invalid.
    """
    global next_id
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'message': 'Invalid request payload'}), 400
    item = {'id': next_id, 'name': data['name']}
    items[next_id] = item
    next_id += 1
    return jsonify(item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Handles PUT requests to update an existing item by ID.
    Expects a JSON request body with 'name'.
    Args:
        item_id: The ID of the item to update.
    Returns:
        JSON response with the updated item and a 200 status code if successful,
        or a JSON error message and a 404 status code if the item is not found,
        or a JSON error message and a 400 status code if the request is invalid.
    """
    item = items.get(item_id)
    if not item:
        return jsonify({'message': 'Item not found'}), 404.
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'message': 'Invalid request payload'}), 400
    item['name'] = data['name']
    return jsonify(item), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """
    Handles DELETE requests to delete an item by ID.
    Args:
        item_id: The ID of the item to delete.
    Returns:
        JSON response with the deleted item and a 200 status code if successful,
        or a JSON error message and a 404 status code if the item is not found.
    """
    item = items.pop(item_id, None)
    if item:
        return jsonify(item), 200
    return jsonify({'message': 'Item not found'}), 404.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')