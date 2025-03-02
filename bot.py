from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters
import sqlite3
import logging

# Токен вашего бота
TOKEN = '7573108834:AAG8Br5kw8B7NOUZJpiJge-IfIR_xFLUuZU'

# Ссылка на ваш сайт в формате Web App
WEB_APP_URL = 'https://werdsaf.github.io/site/'

# Путь к файлу базы данных SQLite
DATABASE_FILE = 'telegram_bot.db'

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для подключения к базе данных
def get_db_connection():
    return sqlite3.connect(DATABASE_FILE)

# Функция для создания таблицы пользователей (если она не существует)
def create_users_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        username TEXT,
        display_name TEXT,
        timezone TEXT,
        work_hours TEXT
    )
    """
    try:
        cursor.execute(query)
        connection.commit()
        logger.info("Таблица 'users' создана или уже существует.")
    except sqlite3.Error as err:
        logger.error(f"Ошибка при создании таблицы: {err}")
    finally:
        cursor.close()
        connection.close()

# Функция для сохранения пользователя в базе данных
def save_user(user_id, username, display_name, timezone, work_hours):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """
    INSERT INTO users (user_id, username, display_name, timezone, work_hours)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
    username = excluded.username,
    display_name = excluded.display_name,
    timezone = excluded.timezone,
    work_hours = excluded.work_hours
    """
    try:
        cursor.execute(query, (user_id, username, display_name, timezone, work_hours))
        connection.commit()
        logger.info(f"Пользователь {user_id} сохранен в базе данных.")
    except sqlite3.Error as err:
        logger.error(f"Ошибка при сохранении пользователя: {err}")
    finally:
        cursor.close()
        connection.close()

# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    username = user.username
    display_name = user.full_name

    # Сохраняем пользователя в базе данных
    save_user(user_id, username, display_name, 'UTC+00', '09:00-17:00')

    # Отправляем меню с кнопками
    await show_menu(update)

# Функция для отображения меню с кнопками
async def show_menu(update: Update):
    keyboard = [
        [KeyboardButton("Открыть веб-приложение", web_app={'url': WEB_APP_URL})],
        [KeyboardButton("Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Обработчик для кнопки "Помощь"
async def handle_help_button(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Этот бот позволяет открывать веб-приложение. "
        "Используйте кнопку 'Открыть веб-приложение', чтобы начать."
    )

# Обработчик для текстовых сообщений
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    if text == "Помощь":
        await handle_help_button(update, context)
    else:
        await update.message.reply_text("Используйте кнопки для взаимодействия с ботом.")

# Обработчик ошибок
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Ошибка: {context.error}")

# Основная функция для запуска бота
def main():
    # Проверяем подключение к SQLite и создаем таблицу
    create_users_table()

    # Создаем приложение бота
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()