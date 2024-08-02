# Home Assistant Kaufland Shoppinglist

Install requests, websocket, dotenv via pip

Create .env file with the following contents

### Home Assistant configuration

HOME_ASSISTANT_GET=ws://homeassistant.local:8123/api/websocket
HOME_ASSISTANT_ADD=http://homeassistant.local:8123/api/services/todo/add_item
HOME_ASSISTANT_REMOVE=http://homeassistant.local:8123/api/services/todo/remove_item
HOME_ASSISTANT_TOKEN=
HOME_ASSISTANT_TODO_NAME=todo.xxx

### Kaufland configuration

KAUFLAND_URL=
KAUFLAND_COOKIE=
KAUFLAND_SLEEP=600 # in seconds

Run py import.py
