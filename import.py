import os
import json
import time
import requests
from dotenv import load_dotenv
from websocket import create_connection

# Load environment variables from .env file
load_dotenv()

# Home Assistant configuration
home_assistant = {
    'get': os.getenv('HOME_ASSISTANT_GET'),
    'add': os.getenv('HOME_ASSISTANT_ADD'),
    'remove': os.getenv('HOME_ASSISTANT_REMOVE'),
    'token': os.getenv('HOME_ASSISTANT_TOKEN'),
    'todo_name': os.getenv('HOME_ASSISTANT_TODO_NAME'),
    'notify_url': os.getenv('HOME_ASSISTANT_NOTIFY_URL')
}

# Kaufland configuration
kaufland = {
    'url': os.getenv('KAUFLAND_URL'),
    'cookie': os.getenv('KAUFLAND_COOKIE'),
    'sleep': os.getenv('KAUFLAND_SLEEP')
}


def get_headers():
    # Returns headers needed for API requests, including the Authorization token
    return {
        'Authorization': f'Bearer {home_assistant["token"]}',
        'Content-Type': 'application/json'
    }


def send_notification(message, title="Kaufland Shopping List Error"):
    # Sends a notification message to the Home Assistant notify URL
    response = requests.post(home_assistant['notify_url'], headers=get_headers(), json={
                             'message': message, 'title': title})
    if response.status_code == 200:
        print(f"Notification sent: {message}")
    else:
        print("Error sending notification:" +
              f"{response.status_code} - {response.text}")


def fetch_json_response(url, headers):
    # Fetches JSON data from a URL and handles potential errors
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_message = f"Error fetching data: {str(e)}"
        print(error_message)
        send_notification(error_message)
        return {}


def get_todo_list():
    # Retrieves the to-do list from Home Assistant via WebSocket
    try:
        ws = create_connection(home_assistant['get'])
        ws.send(json.dumps(
            {"type": "auth", "access_token": home_assistant['token']}))
        ws.recv()  # Read the auth response
        ws.recv()  # Read the auth response
        ws.send(json.dumps({
            "type": "call_service",
            "domain": "todo",
            "service": "get_items",
            "target": {"entity_id": home_assistant["todo_name"]},
            "id": 1,
            "return_response": True
        }))
        result = json.loads(ws.recv())
        ws.close()
        return result
    except Exception as e:
        error_message = f"Error getting to-do list: {str(e)}"
        print(error_message)
        send_notification(error_message)
        return {}


def modify_item(action, item_name):
    # Modifies an item in the to-do list (either add or remove)
    try:
        url = home_assistant[action]
        payload = {'entity_id': home_assistant['todo_name'], 'item': item_name}
        response = requests.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        print(f"Item '{item_name}' successfully {action.replace('_', ' ')}.")
    except requests.RequestException as e:
        error_message = f"Error {action.replace('_', ' ')} item '{
            item_name}': {str(e)}"
        print(error_message)
        send_notification(error_message)


def fetch_external_data():
    # Fetches external data from Kaufland
    headers = {'Cookie': f'{kaufland["cookie"]}',
               'Content-Type': 'application/json'}
    return fetch_json_response(kaufland['url'], headers)


def main():
    # Main function to handle the overall process
    # Fetch external data from Kaufland
    external_data = fetch_external_data()
    if not external_data:
        print("No external data fetched.")
        return  # Exit if no external data is available

    # Retrieve the current to-do list from Home Assistant
    todo_list = get_todo_list()
    if not todo_list:
        print("No to-do list fetched.")
        return  # Exit if the to-do list could not be retrieved

    print(f"Todo List: {todo_list}")

    # Extract items from the to-do list
    items = todo_list.get('result', {}).get('response', {}).get(
        home_assistant["todo_name"], {}).get('items', [])

    # Check if there are items to remove
    if not items:
        print("No items found to remove.")

    # Process each item in the to-do list to remove it
    for item in items:
        # Get the unique identifier of the item
        uid = item.get('uid', 'Unknown UID')
        print(f"Attempting to remove item: {uid}")
        modify_item('remove', uid)  # Remove the item from the to-do list

    # Process each item in the external data to add it to the to-do list
    for item in external_data.get('results', []):
        # Check if the item has been marked as deleted
        if item.get('deleted', False):
            doc = item.get('doc', {})
            title = doc.get('title', 'No title')
            print(f"Skipping deleted item: {title}")
            continue  # Skip this item and move to the next

        doc = item.get('doc', {})
        title = doc.get('title', 'No title')  # Get the title of the item
        subtitle = doc.get('subtitle', '')  # Get the subtitle of the item
        # Get the number of items
        number_of_items = doc.get('numberOfItems', 0)

        # Format the item text for adding to the to-do list
        item_text = f"{title} {subtitle} ({number_of_items}x)"
        print(f"Attempting to add item: {item_text}")
        modify_item('add', item_text)  # Add the item to the to-do list


if __name__ == "__main__":
    while True:
        main()  # Call the main function to execute the process
        # Get the sleep duration from configuration
        wait_time_seconds = int(kaufland['sleep'])
        # Print the wait time
        print(f"Waiting for {wait_time_seconds / 60:.2f} minutes.")
        # Pause execution for the specified duration
        time.sleep(wait_time_seconds)
