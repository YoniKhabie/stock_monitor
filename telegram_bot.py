import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()
BASE_URL = "https://api.telegram.org/bot"
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

async def send_message_to_group(text):
    bot = Bot(token=BOT_TOKEN)
    try:
        bot.send_message(chat_id=GROUP_CHAT_ID, text=text, disable_notification=False)
        print("Message sent successfully.")
    except TelegramError as e:
        print(f"Failed to send message: {e}")

if __name__ == "__main__":
    asyncio.run(send_message_to_group("Hello group! This is a secure message from the bot."))