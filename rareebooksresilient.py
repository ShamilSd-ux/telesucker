import asyncio
import yaml
from telethon import TelegramClient, events
from telethon.tl.types import MessageService
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION_NAME", "forward_bot")

# Load forwarding configuration from YAML file
def load_forward_config(file_path="forward_config.yaml"):
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            return {
                entry["source"]: entry["destinations"]
                for entry in data.get("forward_config", [])
            }
    except Exception as e:
        print(f"Error loading forwarding config: {e}")
        return {}

async def main():
    # Fetch forwarding configurations
    forward_config = load_forward_config()

    # Initialize the Telegram client
    async with TelegramClient(SESSION, API_ID, API_HASH) as client:
        print("Bot is running...")

        @client.on(events.NewMessage(chats=list(forward_config.keys())))
        async def handler(event):
            # Skip service messages (e.g., user joined, pinned a message)
            if isinstance(event.message, MessageService):
                return

            source = event.chat_id
            if source in forward_config:
                for destination in forward_config[source]:
                    try:
                        # Check if the message contains text
                        if event.message.text:
                            # Send the text as a new message to the destination
                            await client.send_message(destination, event.message.text)
                        # Check if the message contains media (e.g., photos, videos)
                        elif event.message.media:
                            # Send the media as a new message to the destination
                            await client.send_file(destination, event.message.media, caption=event.message.message)
                        print(f"Copied message from {source} to {destination}")
                    except Exception as e:
                        print(f"Failed to copy message to {destination}: {e}")

        await client.run_until_disconnected()

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
