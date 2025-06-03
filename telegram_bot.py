import asyncio
import os

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

async def send_message_to_group(text):
    try:
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
        # print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")
        # print(f"GROUP_CHAT_ID exists: {bool(GROUP_CHAT_ID)}")
        if not BOT_TOKEN or not GROUP_CHAT_ID:
            raise ValueError("Missing Telegram credentials in environment variables")
            
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(
            chat_id=int(GROUP_CHAT_ID),
            text=text,
            disable_notification=False
        )
        print("Message sent successfully.")
    except Exception as e:
        print(f"Failed to send message: {e}")
        raise  # Re-raise to fail the workflow