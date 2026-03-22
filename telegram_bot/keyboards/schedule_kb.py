"""Schedule-specific keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def confirm_delete(time: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton('✅ Да, удалить', callback_data=f'sched_confirm_del_{time}'),
            InlineKeyboardButton('❌ Отмена', callback_data='schedule'),
        ]
    ])
