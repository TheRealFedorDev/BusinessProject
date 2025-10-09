import asyncio
import logging


from aiogram import Bot, Dispatcher, F, types
from aiogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# ----------- Конфигурация -----------
BOT_TOKEN = "8300721286:AAEYEf1fdWAOOI-lzifAG4u3xKsckXgPY7k"
ADMIN_CHAT_ID = "5567849989"  # твой Telegram ID для уведомлений

# ----------- Логирование -----------
logging.basicConfig(level=logging.INFO)

# ----------- Инициализация -----------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
# ----------- Функции -----------

def get_catalog_text():
    return (
        "💼 <b>Прайс-лист на услуги:</b>\n\n"
        "🤖 <b>Разработка Telegram-ботов под ключ</b> — от <b>500 ₽</b>\n"
        "  • Подключение БД, админки, меню, inline-кнопок.\n"
        "  • Возможна интеграция с API / CRM / сайтами.\n\n"
        "🧠 <b>Создание AI-ботов (OpenAI / GPT-интеграция)</b> — от <b>1 000 ₽</b>\n"
        "  • Встроенный ИИ с памятью и логикой.\n"
        "  • Возможен кастомный fine-tuning под заказ.\n\n"
        "  • Ежемесячная оплата ИИ зависит от выбранного вами плана (Цена предоставлена за подключение). \n"
        "🏪 <b>Настройка ботов-магазинов и CRM</b> — от <b>2 000 ₽</b>\n"
        "  • Поддержка корзины, оплат, панели администратора.\n"
        "  • Интеграции с Telegram Pay, YooMoney, CryptoBot.\n\n"
        "⚙️ <b>Парсеры, автоматизация, Python-скрипты</b> — от <b>2 500 ₽</b>\n"
        "  • Сбор данных, отчёты, API-интеграции, автопостинг.\n\n"
        "💬 Связаться со мной — кнопка ниже 👇"
    )

# ----------- Подготовка -----------
async def setup_main_menu(bot: Bot):
    """Создает кнопку 'Menu' с командой /start"""
    commands = [
        BotCommand(command="start", description="🔹 Главное меню"),
        BotCommand(command="links", description="🔹 Ссылки"),
    ]
    await bot.set_my_commands(commands)


# ----------- /start -----------


@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я — твой персональный бот от имени Фёдора.\n"
        "Вот что я могу сделать:",
        reply_markup=get_main_menu()
    )


# ----------- /links -----------
def get_main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧠 Мои возможности", callback_data="catalog"),
            ],
            [
                InlineKeyboardButton(text="💬 Мой Telegram", url="https://t.me/acbfdhg"),
                InlineKeyboardButton(text="💻 GitHub", url="https://github.com/TheRealFedorDev"),
            ],
        ]
    )
    return keyboard
def get_links_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Мой Telegram", url="https://t.me/acbfdhg"),
                InlineKeyboardButton(text="💻 GitHub", url="https://github.com/TheRealFedorDev"),
            ]
        ]
    )
    return keyboard

@dp.message(F.text == "/links")
async def send_links(message: types.Message):
    await message.answer("📎 Мои ссылки:", reply_markup=get_links_menu())


# ----------- Обработка заказов -----------

@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    await callback.message.edit_text(
        get_catalog_text(),
        reply_markup=get_links_menu(),
        parse_mode="HTML"
    )

# ----------- Обработка любых других сообщений -----------
@dp.message()  # ловим все сообщения
async def unknown_message(message: types.Message):
    # Можно просто уведомить пользователя
    await message.answer(
        "❌ Извините, я не понял ваш запрос.\n"
    )

    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я — твой персональный бот от имени Фёдора.\n"
        "Вот что я могу сделать:",
        reply_markup=get_main_menu()
    )


# ----------- Запуск бота -----------
async def main():
    await setup_main_menu(bot)
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
