
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = os.environ.get("TELEGRAM_API_ID")
API_HASH = os.environ.get("TELEGRAM_API_HASH")

if not API_ID or not API_HASH:
    print("Error: TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables must be set.")
    exit(1)

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("Your session string is:", client.session.save())
