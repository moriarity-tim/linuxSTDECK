import pytest
import requests

# Assuming the API runs on localhost:5000 for testing purposes
BASE_URL = 'http://localhost:5000'

def test_get_items_empty():
    """Tests GET /items when the items list is empty."""
    response = requests.get(f'{BASE_URL}/items')
    assert response.status_code == 200
    assert response.json() == []

def test_create_item():
    """Tests POST /items to create a new item."""
    item_data = {'name': 'New Item'}
    response = requests.post(f'{BASE_URL}/items', json=item_data)
    assert response.status_code == 201
    created_item = response.json()
    assert created_item['name'] == 'New Item'
    assert 'id' in created_item

def test_get_item():
    """Tests GET /items/<id> to retrieve a specific item."""
    # First, create an item to retrieve
    item_data = {'name': 'Item to Get'}
    create_response = requests.post(f'{BASE_URL}/items', json=item_data)
    created_item_id = create_response.json()['id']

    response = requests.get(f'{BASE_URL}/items/{created_item_id}')
    assert response.status_code == 200
    retrieved_item = response.json()
    assert retrieved_item['id'] == created_item_id
    assert retrieved_item['name'] == 'Item to Get'

def test_get_nonexistent_item():
    """Tests GET /items/<id> for a non-existent item."""
    response = requests.get(f'{BASE_URL}/items/999') # Assuming 999 doesn't exist
    assert response.status_code == 404.
    assert 'Item not found' in response.json().get('message', '')

def test_update_item():
    """Tests PUT /items/<id> to update an existing item."""
    # First, create an item to update
    item_data = {'name': 'Item to Update'}
    create_response = requests.post(f'{BASE_URL}/items', json=item_data)
    item_id_to_update = create_response.json()['id']

    updated_data = {'name': 'Updated Item Name'}
    response = requests.put(f'{BASE_URL}/items/{item_id_to_update}', json=updated_data)
    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item['id'] == item_id_to_update
    assert updated_item['name'] == 'Updated Item Name'

def test_update_nonexistent_item():
    """Tests PUT /items/<id> for a non-existent item."""
    updated_data = {'name': 'Updated Item Name'}
    response = requests.put(f'{BASE_URL}/items/999', json=updated_data) # Assuming 999 doesn't exist
    assert response.status_code == 404.
    assert 'Item not found' in response.json().get('message', '')

def test_delete_item():
    """Tests DELETE /items/<id> to delete an item."""
    # First, create an item to delete
    item_data = {'name': 'Item to Delete'}
    create_response = requests.post(f'{BASE_URL}/items', json=item_data)
    item_id_to_delete = create_response.json()['id']

    response = requests.delete(f'{BASE_URL}/items/{item_id_to_delete}')
    assert response.status_code == 200
    deleted_item = response.json()
    assert deleted_item['id'] == item_id_to_delete
    assert deleted_item['name'] == 'Item to Delete'

    # Verify that the item is no longer available
    get_response = requests.get(f'{BASE_URL}/items/{item_id_to_delete}')
    assert get_response.status_code == 404.

def test_delete_nonexistent_item():
    """Tests DELETE /items/<id> for a non-existent item."""
    response = requests.delete(f'{BASE_URL}/items/999') # Assuming 999 doesn't exist
    assert response.status_code == 404.
    assert 'Item not found' in response.json().get('message', '')