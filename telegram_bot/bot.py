"""CatFeed Pro — Telegram Bot with Mini App (Remote Control / Пульт управления).

The bot serves a web-based Mini App for full device control,
while also supporting classic text commands as fallback.
"""
import asyncio
import os
import logging
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, MenuButtonWebApp
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters,
)
import config
from handlers.start import start_handler, help_handler
from handlers.status import status_handler
from handlers.feed import feed_handler, feed_callback
from handlers.schedule import (
    schedule_handler, schedule_delete_callback,
    schedule_confirm_delete_callback, schedule_add_callback,
    schedule_add_time, schedule_add_cancel, WAITING_TIME,
)
from handlers.stats import stats_handler, stats_period_callback
from handlers.events import events_handler
from handlers.settings import (
    settings_handler, setting_callback, setting_value_handler,
    setting_cancel, WAITING_VALUE,
)
from keyboards.main_menu import main_menu
from services.notifications import notification_loop, subscribed_chats
from services.api_client import api
from webapp_server import start_webapp_server

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:8080')


async def menu_callback(update, context):
    """Return to main menu."""
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        '🐱 *CatFeed Pro — Главное меню*',
        parse_mode='Markdown',
        reply_markup=main_menu()
    )


async def start_with_webapp(update: Update, context):
    """Send welcome message with Mini App button."""
    subscribed_chats.add(update.effective_chat.id)

    webapp_info = WebAppInfo(url=WEBAPP_URL)

    # Reply keyboard with WebApp button
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton('🐱 Открыть пульт', web_app=webapp_info)]],
        resize_keyboard=True,
    )

    await update.message.reply_text(
        '🐱 *CatFeed Pro — Умная кормушка*\n\n'
        'Нажмите кнопку ниже, чтобы открыть *пульт управления*.\n\n'
        'Также доступны текстовые команды:\n'
        '/status — статус · /feed — покормить\n'
        '/schedule — расписание · /stats — статистика\n'
        '/events — события · /settings — настройки',
        parse_mode='Markdown',
        reply_markup=keyboard,
    )

    # Set Menu Button to Mini App
    try:
        await context.bot.set_chat_menu_button(
            chat_id=update.effective_chat.id,
            menu_button=MenuButtonWebApp(text='Пульт', web_app=webapp_info),
        )
    except Exception as e:
        logger.warning(f'Could not set menu button: {e}')


async def post_init(application: Application):
    """Start notification loop after bot init."""
    asyncio.create_task(notification_loop(application.bot))
    logger.info('Notification loop task created')


async def post_shutdown(application: Application):
    """Cleanup on shutdown."""
    await api.close()


def main():
    if not config.BOT_TOKEN:
        logger.error('TELEGRAM_BOT_TOKEN not set!')
        return

    # Start webapp HTTP server
    start_webapp_server()

    app = Application.builder().token(config.BOT_TOKEN).post_init(post_init).post_shutdown(post_shutdown).build()

    # Schedule conversation (for adding time)
    sched_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(schedule_add_callback, pattern='^sched_add$')],
        states={
            WAITING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_add_time)],
        },
        fallbacks=[CommandHandler('cancel', schedule_add_cancel)],
        per_message=False,
    )

    # Settings conversation (for setting values)
    settings_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(setting_callback, pattern='^set_')],
        states={
            WAITING_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, setting_value_handler)],
        },
        fallbacks=[CommandHandler('cancel', setting_cancel)],
        per_message=False,
    )

    # Conversation handlers first
    app.add_handler(sched_conv)
    app.add_handler(settings_conv)

    # /start opens Mini App
    app.add_handler(CommandHandler('start', start_with_webapp))
    app.add_handler(CommandHandler('help', help_handler))

    # Text command fallbacks
    app.add_handler(CommandHandler('status', status_handler))
    app.add_handler(CommandHandler('feed', feed_handler))
    app.add_handler(CommandHandler('schedule', schedule_handler))
    app.add_handler(CommandHandler('stats', stats_handler))
    app.add_handler(CommandHandler('events', events_handler))
    app.add_handler(CommandHandler('settings', settings_handler))

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(menu_callback, pattern='^menu$'))
    app.add_handler(CallbackQueryHandler(status_handler, pattern='^status$'))
    app.add_handler(CallbackQueryHandler(feed_handler, pattern='^feed$'))
    app.add_handler(CallbackQueryHandler(feed_callback, pattern=r'^feed_\d+$'))
    app.add_handler(CallbackQueryHandler(schedule_handler, pattern='^schedule$'))
    app.add_handler(CallbackQueryHandler(schedule_delete_callback, pattern=r'^sched_del_'))
    app.add_handler(CallbackQueryHandler(schedule_confirm_delete_callback, pattern=r'^sched_confirm_del_'))
    app.add_handler(CallbackQueryHandler(stats_handler, pattern='^stats$'))
    app.add_handler(CallbackQueryHandler(stats_period_callback, pattern=r'^stats_(day|week|month)$'))
    app.add_handler(CallbackQueryHandler(events_handler, pattern='^events$'))
    app.add_handler(CallbackQueryHandler(settings_handler, pattern='^settings$'))

    logger.info(f'Starting CatFeed Pro Bot (Mini App: {WEBAPP_URL})')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
