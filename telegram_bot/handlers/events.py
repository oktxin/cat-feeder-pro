"""Events handler."""
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from services.api_client import api
from keyboards.main_menu import back_menu

EVENT_ICONS = {
    'feeding_complete': '✅',
    'cat_detected': '🐱',
    'cat_left': '👋',
    'low_food_warning': '⚠️',
    'low_water_warning': '💧',
    'error': '❌',
}


async def events_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()

    events = await api.get_events(limit=15)
    if not events:
        text = '📋 Нет событий'
    else:
        text = '📋 *Последние события:*\n\n'
        for e in events[:15]:
            etype = e.get('type', '')
            icon = EVENT_ICONS.get(etype, '📌')
            ts = e.get('timestamp', e.get('createdAt', ''))
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                time_str = dt.strftime('%d.%m %H:%M')
            except Exception:
                time_str = ts[:16] if ts else '—'
            text += f'{icon} `{time_str}` {etype.replace("_", " ")}\n'

    if update.callback_query:
        await msg.edit_text(text, parse_mode='Markdown', reply_markup=back_menu())
    else:
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=back_menu())
