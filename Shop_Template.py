import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import LabeledPrice

BOT_TOKEN = "ВАШ_ТОКЕН"
PAYMENT_PROVIDER_TOKEN = "ВАШ_PROVIDER_TOKEN"
CURRENCY = "RUB"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

PRODUCTS = {"Книга": 500, "Футболка": 1200}

@dp.message(F.text == "/shop")
async def shop(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for name, price in PRODUCTS.items():
        keyboard.add(types.InlineKeyboardButton(f"{name} - {price}₽", callback_data=f"buy_{name}"))
    await message.answer("Выберите товар:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy(callback: types.CallbackQuery):
    item = callback.data.split("_")[1]
    price = [LabeledPrice(label=item, amount=PRODUCTS[item]*100)]
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=item,
        description=f"Покупка {item}",
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency=CURRENCY,
        prices=price,
        start_parameter="shop",
        payload=item
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())