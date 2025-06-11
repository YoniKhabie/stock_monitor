import os
from datetime import datetime
from io import BytesIO

from dotenv import load_dotenv
from telegram import Bot, InputFile

load_dotenv()

class MyBot:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        self.GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
        if not self.BOT_TOKEN or not self.GROUP_CHAT_ID:
            raise ValueError("Missing Telegram credentials in environment variables")
        self.bot = Bot(token=self.BOT_TOKEN)

    async def send_message_to_group(self, text):
        try:
            await self.bot.send_message(
                chat_id=int(self.GROUP_CHAT_ID),
                text=text,
                disable_notification=False
            )
            print("Message sent successfully.")
        except Exception as e:
            print(f"Failed to send message: {e}")
            raise

    async def send_img_to_group(self, image_buf: BytesIO, caption: str = ""):
        try:
            await self.bot.send_photo(
                chat_id=int(self.GROUP_CHAT_ID),
                photo=image_buf,
                caption=caption,
                disable_notification=False
            )
            print("High-quality image sent successfully.")
        except Exception as e:
            print(f"Failed to send image: {e}")
            raise