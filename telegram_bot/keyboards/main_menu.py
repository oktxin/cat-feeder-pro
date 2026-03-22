"""Inline keyboard builders."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton('📊 Статус', callback_data='status'),
            InlineKeyboardButton('🍽 Покормить', callback_data='feed'),
        ],
        [
            InlineKeyboardButton('📅 Расписание', callback_data='schedule'),
            InlineKeyboardButton('📈 Статистика', callback_data='stats'),
        ],
        [
            InlineKeyboardButton('📋 События', callback_data='events'),
            InlineKeyboardButton('⚙️ Настройки', callback_data='settings'),
        ],
    ])


def feed_portions() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton('20г', callback_data='feed_20'),
            InlineKeyboardButton('30г', callback_data='feed_30'),
            InlineKeyboardButton('50г', callback_data='feed_50'),
        ],
        [
            InlineKeyboardButton('70г', callback_data='feed_70'),
            InlineKeyboardButton('100г', callback_data='feed_100'),
        ],
        [InlineKeyboardButton('↩ Меню', callback_data='menu')],
    ])


def back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('↩ Меню', callback_data='menu')],
    ])


def stats_periods() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton('День', callback_data='stats_day'),
            InlineKeyboardButton('Неделя', callback_data='stats_week'),
            InlineKeyboardButton('Месяц', callback_data='stats_month'),
        ],
        [InlineKeyboardButton('↩ Меню', callback_data='menu')],
    ])


def schedule_menu(times: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for t in times:
        buttons.append([
            InlineKeyboardButton(f'🕐 {t}', callback_data=f'sched_info_{t}'),
            InlineKeyboardButton('❌', callback_data=f'sched_del_{t}'),
        ])
    buttons.append([InlineKeyboardButton('➕ Добавить время', callback_data='sched_add')])
    buttons.append([InlineKeyboardButton('↩ Меню', callback_data='menu')])
    return InlineKeyboardMarkup(buttons)
