import requests
from aiogram import Bot, Dispatcher, types, executor

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.reply("Привет! Напиши название города 🌆")

@dp.message_handler()
async def weather(msg: types.Message):
    city = msg.text
    url = f"https://wttr.in/{city}?format=%t"
    temp = requests.get(url).text
    await msg.reply(f"Температура в {city}: {temp}")

executor.start_polling(dp)
