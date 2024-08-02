# Home Assistant Kaufland Shoppinglist

Create .env file with the following contents

```
### Home Assistant configuration

HOME_ASSISTANT_GET=ws://homeassistant.local:8123/api/websocket
HOME_ASSISTANT_ADD=http://homeassistant.local:8123/api/services/todo/add_item
HOME_ASSISTANT_REMOVE=http://homeassistant.local:8123/api/services/todo/remove_item
HOME_ASSISTANT_TOKEN=
HOME_ASSISTANT_TODO_NAME=todo.xxx

### Kaufland configuration

KAUFLAND_URL=https://sync.kaufland.de/sync_klapp/_changes?include_docs=true&feed=longpoll
KAUFLAND_COOKIE=
KAUFLAND_SLEEP=600 # in seconds
```

Create a Kaufland Account, open Dev Tools (F12) and search for `https://sync.kaufland.de/sync_klapp/_changes?include_docs=true&feed=longpoll&heartbeat=xxx&since=xxx`. Copy the included cookie in the request header and insert it to the .env.

Create a new Home Assistant todo list (IMPORTANT: Only use the todo list for this script! All items get deleted every x mins!)

Optional: Create Home Assistant user for the token

Insert Home Assistant token and todo name into the .env

Install requests, websocket, dotenv via `pip install -r requirements.txt`

Run py import.py

### Script will check if your Kaufland shopping list has been updated, delete the previous Home Assistant shopping list and push the new items to it.
