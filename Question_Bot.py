import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Настройки
API_TOKEN = "8511295355:AAERVtV2oHMlVuo8aXR2GUTQ5bNsTl-lLek"

# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Состояния для опроса
class Questionnaire(StatesGroup):
    name = State()
    phone = State()
    email = State()


# Создаем главное меню
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📝 Начать опрос"))
    builder.add(KeyboardButton(text="📊 Статистика"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# Клавиатура для отмены
def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить опрос")]],
        resize_keyboard=True
    )


# Инлайн-клавиатура для быстрых действий
def get_inline_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🚀 Начать опрос", callback_data="start_survey"))
    builder.add(InlineKeyboardButton(text="📈 Статистика", callback_data="show_stats"))
    builder.add(InlineKeyboardButton(text="❓ Помощь", callback_data="show_help"))
    builder.adjust(2)
    return builder.as_markup()


# Инициализация базы данных
def init_database():
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)
        ''')

        conn.commit()
        conn.close()
        logging.info("✅ База данных SQLite инициализирована успешно")

    except Exception as e:
        logging.error(f"❌ Ошибка инициализации базы данных: {e}")


# Сохранение данных в базу
def save_to_database(user_data: dict, telegram_user):
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users 
            (user_id, username, first_name, last_name, name, phone, email) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            telegram_user.id,
            telegram_user.username,
            telegram_user.first_name,
            telegram_user.last_name,
            user_data['name'],
            user_data['phone'],
            user_data['email']
        ))

        conn.commit()
        conn.close()
        logging.info(f"✅ Данные пользователя {telegram_user.id} сохранены")

    except Exception as e:
        logging.error(f"❌ Ошибка сохранения в базу данных: {e}")
        raise


# Получение статистики
def get_stats():
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE DATE(created_at) = DATE('now')
        ''')
        today_users = cursor.fetchone()[0]

        conn.close()
        return total_users, today_users

    except Exception as e:
        logging.error(f"❌ Ошибка получения статистики: {e}")
        return 0, 0


# Команда /start - главное меню
@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "🤖 <b>Добро пожаловать в бот-опросник!</b>\n\n"
        "Я помогу собрать информацию о пользователях.\n"
        "Выберите действие из меню ниже:"
    )

    await message.answer(welcome_text, reply_markup=get_main_menu())
    await message.answer("Или используйте быстрые кнопки:", reply_markup=get_inline_menu())


# Обработка кнопки "Начать опрос"
@dp.message(F.text == "📝 Начать опрос")
async def start_survey_button(message: Message, state: FSMContext):
    await state.set_state(Questionnaire.name)
    await message.answer(
        "👋 Отлично! Давайте начнем опрос.\n\n"
        "Как вас зовут? (Введите ваше имя)",
        reply_markup=get_cancel_keyboard()
    )


# Обработка кнопки "Статистика"
@dp.message(F.text == "📊 Статистика")
async def stats_button(message: Message):
    total_users, today_users = get_stats()

    stats_text = (
        f"📊 <b>Статистика бота:</b>\n\n"
        f"• 👥 Всего пользователей: <b>{total_users}</b>\n"
        f"• 📈 Сегодня: <b>{today_users}</b>\n"
        f"• 🚀 Бот активен и готов к работе!"
    )

    await message.answer(stats_text, reply_markup=get_main_menu())


# Обработка кнопки "Помощь"
@dp.message(F.text == "ℹ️ Помощь")
async def help_button(message: Message):
    help_text = (
        "🤖 <b>Справка по боту:</b>\n\n"
        "<b>Основные команды:</b>\n"
        "• 📝 <b>Начать опрос</b> - заполнить анкету\n"
        "• 📊 <b>Статистика</b> - посмотреть статистику\n"
        "• ℹ️ <b>Помощь</b> - эта справка\n\n"
        "<b>Команды в чате:</b>\n"
        "• /start - главное меню\n"
        "• /stats - статистика\n"
        "• /help - справка\n"
        "• /cancel - отмена опроса"
    )

    await message.answer(help_text, reply_markup=get_main_menu())


# Обработка кнопки отмены
@dp.message(F.text == "❌ Отменить опрос")
async def cancel_survey_button(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного опроса для отмены.", reply_markup=get_main_menu())
        return

    await state.clear()
    await message.answer(
        "❌ Опрос отменен.\n"
        "Вы вернулись в главное меню.",
        reply_markup=get_main_menu()
    )


# Обработка инлайн-кнопок
@dp.callback_query(F.data == "start_survey")
async def inline_start_survey(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Questionnaire.name)
    await callback.message.edit_text("Опрос начат!")
    await callback.message.answer(
        "👋 Как вас зовут? (Введите ваше имя)",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "show_stats")
async def inline_show_stats(callback: types.CallbackQuery):
    total_users, today_users = get_stats()

    stats_text = (
        f"📊 <b>Статистика:</b>\n"
        f"Всего: {total_users} | Сегодня: {today_users}"
    )

    await callback.message.edit_text(stats_text, reply_markup=get_inline_menu())
    await callback.answer()


@dp.callback_query(F.data == "show_help")
async def inline_show_help(callback: types.CallbackQuery):
    help_text = "🤖 Используйте кнопки ниже для навигации"
    await callback.message.edit_text(help_text, reply_markup=get_inline_menu())
    await callback.answer()


# Получаем имя
@dp.message(Questionnaire.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer(
            '❌ Имя должно содержать хотя бы 2 символа.\n'
            'Попробуйте еще раз:',
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(name=name)
    await state.set_state(Questionnaire.phone)

    await message.answer(
        f'😊 Приятно познакомиться, {name}!\n\n'
        'Теперь введите ваш номер телефона 📞:',
        reply_markup=get_cancel_keyboard()
    )


# Получаем телефон
@dp.message(Questionnaire.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    # Простая валидация телефона
    if len(phone) < 5:
        await message.answer(
            '❌ Пожалуйста, введите корректный номер телефона.\n'
            'Попробуйте еще раз:',
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(Questionnaire.email)

    await message.answer(
        '📧 Отлично! Теперь введите ваш email:',
        reply_markup=get_cancel_keyboard()
    )


# Получаем email и завершаем опрос
@dp.message(Questionnaire.email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip().lower()

    # Простая валидация email
    if '@' not in email or '.' not in email:
        await message.answer(
            '❌ Пожалуйста, введите корректный email.\n'
            'Попробуйте еще раз:',
            reply_markup=get_cancel_keyboard()
        )
        return

    user_data = await state.get_data()
    user_data['email'] = email

    # Сохраняем в базу данных
    try:
        save_to_database(user_data, message.from_user)

        success_text = (
            f'✅ <b>Спасибо за ответы, {user_data["name"]}!</b>\n\n'
            f'📋 <b>Мы сохранили ваши данные:</b>\n'
            f'• 👤 Имя: <b>{user_data["name"]}</b>\n'
            f'• 📞 Телефон: <b>{user_data["phone"]}</b>\n'
            f'• 📧 Email: <b>{user_data["email"]}</b>\n\n'
            f'<i>Скоро с вами свяжутся! 🚀</i>'
        )

        await message.answer(success_text, reply_markup=get_main_menu())

    except Exception as e:
        logging.error(f"❌ Ошибка сохранения данных: {e}")
        await message.answer(
            '❌ Произошла ошибка при сохранении данных.\n'
            'Попробуйте позже или свяжитесь с администратором.',
            reply_markup=get_main_menu()
        )

    await state.clear()


# Команда /cancel для отмены опроса
@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного опроса для отмены.", reply_markup=get_main_menu())
        return

    await state.clear()
    await message.answer(
        "❌ Опрос отменен.\n"
        "Вы вернулись в главное меню.",
        reply_markup=get_main_menu()
    )


# Команда /stats для статистики
@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    total_users, today_users = get_stats()

    stats_text = (
        f"📊 <b>Статистика бота:</b>\n\n"
        f"• 👥 Всего пользователей: <b>{total_users}</b>\n"
        f"• 📈 Сегодня: <b>{today_users}</b>"
    )

    await message.answer(stats_text, reply_markup=get_main_menu())


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🤖 <b>Справка по боту</b>\n\n"
        "Используйте кнопки меню для удобной навигации!\n"
        "Или команды:\n"
        "/start - главное меню\n"
        "/stats - статистика\n"
        "/help - справка\n"
        "/cancel - отмена опроса"
    )

    await message.answer(help_text, reply_markup=get_main_menu())


# Обработка любых других сообщений
@dp.message()
async def echo_message(message: Message):
    await message.answer(
        "🤖 Я бот для опросов!\n\n"
        "Используйте кнопки меню или команды:\n"
        "/start - главное меню\n"
        "/help - справка",
        reply_markup=get_main_menu()
    )


# Запуск бота
async def main():
    init_database()
    logging.info("✅ Бот запущен и готов к работе!")
    print("🤖 Бот запущен! Напишите /start в Telegram")
    print("⏹️  Для остановки нажмите Ctrl+C")

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())