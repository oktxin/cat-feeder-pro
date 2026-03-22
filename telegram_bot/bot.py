"""CatFeed Pro — Telegram Bot (Remote Control / Пульт управления)."""
import asyncio
import logging
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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def menu_callback(update, context):
    """Return to main menu."""
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        '🐱 *CatFeed Pro — Главное меню*',
        parse_mode='Markdown',
        reply_markup=main_menu()
    )


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

    # Add conversation handlers first (they take priority)
    app.add_handler(sched_conv)
    app.add_handler(settings_conv)

    # Command handlers
    app.add_handler(CommandHandler('start', start_handler))
    app.add_handler(CommandHandler('help', help_handler))
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

    logger.info('Starting CatFeed Pro Telegram Bot...')
    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()
