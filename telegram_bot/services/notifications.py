"""Background task that polls events and sends Telegram notifications."""
import asyncio
import logging
from datetime import datetime, timezone
from telegram import Bot
from services.api_client import api
import config

logger = logging.getLogger(__name__)

# Chat IDs that subscribed to notifications
subscribed_chats: set[int] = set()
_last_event_time: str | None = None


EVENT_MESSAGES = {
    'low_food_warning': ('⚠️', 'Мало корма!'),
    'low_water_warning': ('⚠️', 'Мало воды!'),
    'cat_detected': ('🐱', 'Кот обнаружен у кормушки'),
    'cat_left': ('👋', 'Кот ушёл'),
    'feeding_complete': ('✅', 'Кормление завершено'),
    'error': ('❌', 'Ошибка устройства'),
}


async def notification_loop(bot: Bot):
    """Poll events every POLL_INTERVAL seconds, send new ones to subscribed chats."""
    global _last_event_time
    logger.info('Notification loop started')

    while True:
        await asyncio.sleep(config.POLL_INTERVAL)

        if not subscribed_chats:
            continue

        try:
            events = await api.get_events(limit=5)
            if not events:
                continue

            for event in reversed(events):
                event_time = event.get('timestamp', event.get('createdAt', ''))
                if _last_event_time and event_time <= _last_event_time:
                    continue

                etype = event.get('type', '')
                icon, msg = EVENT_MESSAGES.get(etype, ('📌', etype))

                data = event.get('data', {})
                if isinstance(data, str):
                    import json
                    try:
                        data = json.loads(data)
                    except Exception:
                        data = {}

                detail = ''
                if etype == 'feeding_complete':
                    portion = data.get('portion', '?')
                    detail = f' — {portion}г'
                elif etype in ('low_food_warning', 'low_water_warning'):
                    level = data.get('level', data.get('food_level', data.get('water_level', '?')))
                    detail = f' ({level}%)'
                elif etype == 'error':
                    detail = f': {data.get("error_type", "unknown")}'

                text = f'{icon} *{msg}{detail}*'

                for chat_id in subscribed_chats.copy():
                    try:
                        await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown')
                    except Exception as e:
                        logger.warning(f'Failed to notify {chat_id}: {e}')

                _last_event_time = event_time

        except Exception as e:
            logger.error(f'Notification loop error: {e}')
