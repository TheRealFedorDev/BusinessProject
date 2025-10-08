import asyncio
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List

import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv
import os
import openai
from openai import AsyncOpenAI

load_dotenv()


BOT_TOKEN_AI = os.getenv("BOT_TOKEN_AI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


logging.basicConfig(level=logging.INFO)


bot = Bot(token=BOT_TOKEN_AI)
dp = Dispatcher()
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)




@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привет! Я AI-помощник. Задай мне любой вопрос.")




@dp.message()
async def chat(message: Message):
    response = await openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "Ты вежливый AI-консультант Telegram-магазина."},
            {"role": "user", "content": message.text}
        ]
    )
    answer = response.choices[0].message.content
    await message.answer(answer)




async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())