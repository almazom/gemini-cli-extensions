import sys
import os
import asyncio
import logging
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Configure logging
log_file = os.path.join(os.path.dirname(__file__), 'telegram_manager.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StateMachine:
    def __init__(self):
        self.state = "UNINITIALIZED"
        self.transitions = {
            "UNINITIALIZED": ["INITIALIZING"],
            "INITIALIZING": ["ACTIVE", "FAILED"],
            "ACTIVE": ["RECONNECTING", "FAILED", "TERMINATED"],
            "RECONNECTING": ["ACTIVE", "FAILED"],
            "FAILED": ["INITIALIZING", "TERMINATED"],
            "TERMINATED": ["INITIALIZING"],
        }

    def get_state(self):
        return self.state

    def transition_to(self, new_state):
        if new_state in self.transitions.get(self.state, []):
            self.state = new_state
            logging.info(f"State changed: {self.state} -> {new_state}")
        else:
            logging.error(f"Invalid state transition: {self.state} -> {new_state}")
            raise ValueError(f"Invalid state transition: {self.state} -> {new_state}")

class TelegramClientBase:
    def __init__(self, api_id, api_hash, session_string):
        self.client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
        self.state_machine = StateMachine()
        logging.info("Telegram client initialized")

    async def connect(self):
        self.state_machine.transition_to("INITIALIZING")
        logging.info("Connecting to Telegram...")
        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                logging.error("Session not authorized")
                print('ERROR: Session not authorized', file=sys.stderr)
                self.state_machine.transition_to("FAILED")
                return False
            me = await self.client.get_me()
            logging.info(f'Connected as: {me.first_name} {me.last_name or ""} (ID: {me.id})')
            print(f'✅ Connected as: {me.first_name} {me.last_name or ""} (ID: {me.id})')
            self.state_machine.transition_to("ACTIVE")
            return True
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            print(f'ERROR: Connection failed: {e}', file=sys.stderr)
            self.state_machine.transition_to("FAILED")
            return False

    async def disconnect(self):
        logging.info("Disconnecting from Telegram...")
        if self.client:
            await self.client.disconnect()
        logging.info("Disconnected.")
        self.state_machine.transition_to("TERMINATED")

class TelegramReader(TelegramClientBase):
    async def read_channel_messages(self, channel, limit=10):
        logging.info(f"Reading messages from channel: {channel}, limit: {limit}")
        try:
            messages = []
            entity = await self.client.get_entity(channel)
            async for message in self.client.iter_messages(entity, limit=limit):
                if message.text:
                    messages.append(message.text)
            logging.info(f"Found {len(messages)} messages")
            return messages
        except Exception as e:
            logging.error(f"Failed to read from {channel}: {e}")
            print(f'ERROR: Failed to read from {channel}: {e}', file=sys.stderr)
            return None

class TelegramSender(TelegramClientBase):
    async def send_message(self, channel, message):
        logging.info(f"Sending message to channel: {channel}")
        try:
            entity = await self.client.get_entity(channel)
            await self.client.send_message(entity, message)
            logging.info("Message sent successfully")
            return True
        except Exception as e:
            logging.error(f"Send failed: {e}")
            print(f'ERROR: Send failed: {e}', file=sys.stderr)
            return False

class TelegramManager:
    def __init__(self, argv):
        self.argv = argv

    def run(self):
        try:
            from telethon.sync import TelegramClient
        except ImportError:
            print("Error: telethon is not installed. Please install it using 'pip install telethon'")
            sys.exit(1)

        load_dotenv()

        API_ID = os.environ.get("TELEGRAM_API_ID")
        API_HASH = os.environ.get("TELEGRAM_API_HASH")
        SESSION_STRING = os.environ.get("TELEGRAM_STRING_SESSION")

        if not API_ID or not API_HASH or not SESSION_STRING:
            print("Error: TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_STRING_SESSION environment variables must be set.")
            sys.exit(1)

        if len(SESSION_STRING) < 200:
            print("ERROR: Session string appears too short", file=sys.stderr)
            sys.exit(1)

        if len(self.argv) == 0:
            print("Usage: python main.py <command> [options]")
            sys.exit(1)

        command = self.argv[0]
        if command == "read":
            if len(self.argv) > 1:
                channel = self.argv[1]
                limit = int(self.argv[2]) if len(self.argv) > 2 else 1
                
                async def run_reader():
                    reader = TelegramReader(API_ID, API_HASH, SESSION_STRING)
                    if not await reader.connect():
                        sys.exit(1)
                    try:
                        messages = await reader.read_channel_messages(channel, limit)
                        if messages is None:
                            sys.exit(1)
                        for message in messages:
                            print(message)
                    finally:
                        await reader.disconnect()

                asyncio.run(run_reader())
            else:
                print("Usage: python main.py read <channel> [limit]")
                sys.exit(1)
        elif command == "send":
            if len(self.argv) > 2:
                channel = self.argv[1]
                message = self.argv[2]
                
                async def run_sender():
                    sender = TelegramSender(API_ID, API_HASH, SESSION_STRING)
                    if not await sender.connect():
                        sys.exit(1)
                    try:
                        if not await sender.send_message(channel, message):
                            sys.exit(1)
                        print("✅ Message sent successfully!")
                    finally:
                        await sender.disconnect()

                asyncio.run(run_sender())
            else:
                print("Usage: python main.py send <channel> <message>")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

if __name__ == "__main__":
    # Activate the virtual environment
    activate_this_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "activate_this.py")
    if os.path.exists(activate_this_file):
        with open(activate_this_file) as f:
            exec(f.read(), dict(__file__=activate_this_file))

    manager = TelegramManager(sys.argv[1:])
    manager.run()