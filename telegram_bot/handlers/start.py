"""Start and help handlers."""
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.main_menu import main_menu
from services.notifications import subscribed_chats


WELCOME = """🐱 *CatFeed Pro — Пульт управления*

Добро пожаловать! Я — бот для управления умной кормушкой.

*Команды:*
/status — текущий статус устройства
/feed — покормить (выбор порции)
/schedule — расписание кормлений
/stats — статистика за период
/events — последние события
/settings — настройки
/help — эта справка

Или используйте меню ниже 👇"""

HELP = """📖 *Справка CatFeed Pro*

*Основные команды:*
• `/status` — уровни корма/воды, батарея, температура, статус мотора
• `/feed` или `/feed 30` — покормить (порция в граммах)
• `/schedule` — просмотр и управление расписанием
• `/stats` — статистика с графиками
• `/events` — последние события устройства
• `/settings` — настройки питомца и порогов

*Уведомления:*
Бот автоматически отправит сообщение при:
⚠️ Низкий уровень корма/воды
🐱 Кот подошёл к кормушке
✅ Кормление завершено
❌ Ошибка устройства"""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribed_chats.add(update.effective_chat.id)
    await update.message.reply_text(WELCOME, parse_mode='Markdown', reply_markup=main_menu())


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, parse_mode='Markdown', reply_markup=main_menu())
