import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types

# ----------- Конфигурация -----------
BOT_TOKEN = "BOT_TOKEN"
ADMIN_CHAT_ID = "ADMIN_USER_TG_ID"  # твой Telegram ID для уведомлений

# ----------- Логирование -----------
logging.basicConfig(level=logging.INFO)

# ----------- Инициализация -----------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------- Меню ресторана -----------
MENU = {
    "Кофе": 150,
    "Чай": 100,
    "Сэндвич": 200,
    "Вилка и Ложка": 0,
}




# ----------- /start -----------
@dp.message(F.text == "/start")
async def start(message: types.Message):
    # Создаём клавиатуру сразу через inline_keyboard
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"{item} - {price}₽", callback_data=f"order_{item}")]
            for item, price in MENU.items()
        ]
    )
    await message.answer("Выберите товар:", reply_markup=keyboard)

# ----------- Обработка заказов -----------
@dp.callback_query(lambda c: c.data.startswith("order_"))
async def handle_order(callback: types.CallbackQuery):
    item = callback.data.split("_")[1]
    price = MENU.get(item, 0)
    user = callback.from_user

    # Отправка подтверждения пользователю
    await bot.send_message(user.id, f"✅ Вы заказали: {item} за {price}₽")

    # Уведомление администратору
    try:
        await bot.send_message(ADMIN_CHAT_ID, f"Новый заказ: {item} от @{user.username}")
    except Exception as e:
        print(f"Не удалось отправить уведомление админу: {e}")

    # Ответ на callback, чтобы убрать "часики" у кнопки
    await callback.answer()

# ----------- Обработка любых других сообщений -----------
@dp.message()  # ловим все сообщения
async def unknown_message(message: types.Message):
    # Можно просто уведомить пользователя
    await message.answer(
        "❌ Извините, я не понял ваш запрос.\n"
        +
        "Пожалуйста, выберите товар из меню ниже."
    )

    # Покажем снова меню
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"{item} - {price}₽", callback_data=f"order_{item}")]
            for item, price in MENU.items()
        ]
    )
    await message.answer("Выберите товар:", reply_markup=keyboard)


# ----------- Запуск бота -----------
async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
