import os
from dotenv import load_dotenv
from websocket import create_connection
import requests
import json
import time

# Load environment variables from .env file
load_dotenv()

# Home Assistant configuration
home_assistant = {
    'get': os.getenv('HOME_ASSISTANT_GET'),
    'add': os.getenv('HOME_ASSISTANT_ADD'),
    'remove': os.getenv('HOME_ASSISTANT_REMOVE'),
    'token': os.getenv('HOME_ASSISTANT_TOKEN'),
    'todo_name': os.getenv('HOME_ASSISTANT_TODO_NAME')
}

# Kaufland configuration
kaufland = {
    'url': os.getenv('KAUFLAND_URL'),
    'cookie': os.getenv('KAUFLAND_COOKIE'),
    'sleep': os.getenv('KAUFLAND_SLEEP')
}


def get_todo_list():
    # Create a WebSocket connection to Home Assistant
    ws = create_connection(home_assistant['get'])

    # Authenticate with Home Assistant
    message = {
        "type": "auth",
        "access_token": home_assistant['token']
    }
    ws.send(json.dumps(message))
    result = ws.recv()
    result = ws.recv()

    # Request the current to-do list
    message = {
        "type": "call_service",
        "domain": "todo",
        "service": "get_items",
        "target": {"entity_id": home_assistant["todo_name"]},
        "id": 1,
        "return_response": True
    }
    ws.send(json.dumps(message))
    result = json.loads(ws.recv())
    ws.close()
    return result


def remove_item(item_name):
    # Remove an item from the to-do list via Home Assistant API
    headers = {
        'Authorization': f'Bearer {home_assistant["token"]}',
        'Content-Type': 'application/json'
    }
    payload = {
        'entity_id': home_assistant['todo_name'],
        'item': item_name
    }
    response = requests.post(
        home_assistant['remove'], headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Item '{item_name}' successfully removed.")
    else:
        print(f"Error removing item: {response.status_code} - {response.text}")


def add_item(item_text):
    # Add a new item to the to-do list via Home Assistant API
    headers = {
        'Authorization': f'Bearer {home_assistant["token"]}',
        'Content-Type': 'application/json'
    }
    payload = {
        'entity_id': home_assistant['todo_name'],
        'item': item_text
    }
    response = requests.post(
        home_assistant['add'], headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Item '{item_text}' successfully added.")
    else:
        print(f"Error adding item: {response.status_code} - {response.text}")


def fetch_external_data():
    # Fetch external data from Kaufland
    headers = {
        'Cookie': f'{kaufland["cookie"]}',
        'Content-Type': 'application/json'
    }
    response = requests.get(kaufland['url'], headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching external data: {response.status_code}")
        return {}


def main():
    # Fetch external data and current to-do list
    external_data = fetch_external_data()
    if not external_data:
        print("No external data fetched.")
        return

    todo_list = get_todo_list()
    if not todo_list:
        print("No to-do list fetched.")
        return

    # Debugging output
    print(f"Todo List: {todo_list}")

    # Remove all existing items from the to-do list
    items = todo_list.get('result', {}).get(
        'response', {}).get(home_assistant["todo_name"], {}).get('items', [])
    if not items:
        print("No items found to remove.")
    for item in items:
        uid = item.get('uid', 'Unknown UID')
        print(f"Attempting to remove item: {uid}")
        remove_item(uid)

    # Add new items to the to-do list, skipping deleted ones
    for item in external_data.get('results', []):
        # Check if the item is marked as deleted
        if item.get('deleted', False):
            doc = item.get('doc', {})
            title = doc.get('title', 'No title')
            print(f"Skipping deleted item: {title}")
            continue

        # Extract item details safely
        doc = item.get('doc', {})
        title = doc.get('title', 'No title')
        subtitle = doc.get('subtitle', '')
        number_of_items = doc.get('numberOfItems', 0)

        item_text = f"{title} {subtitle} ({number_of_items}x)"
        print(f"Attempting to add item: {item_text}")
        add_item(item_text)


if __name__ == "__main__":
    while True:
        main()
        # Calculate wait time in minutes
        wait_time_minutes = int(kaufland['sleep']) / 60
        # Print a message indicating the wait time
        print(f"Waiting for {
              wait_time_minutes} minutes before the next check...")
        # Sleep for x seconds (where x is the sleep time specified in the .env file)
        time.sleep(int(kaufland['sleep']))
