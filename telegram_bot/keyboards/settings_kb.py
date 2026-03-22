"""Settings keyboards."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def settings_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('🐱 Имя питомца', callback_data='set_petname')],
        [InlineKeyboardButton('🍖 Тип корма', callback_data='set_foodtype')],
        [InlineKeyboardButton('⚖ Вес питомца', callback_data='set_petweight')],
        [InlineKeyboardButton('🔔 Порог корма', callback_data='set_food_threshold')],
        [InlineKeyboardButton('💧 Порог воды', callback_data='set_water_threshold')],
        [InlineKeyboardButton('↩ Меню', callback_data='menu')],
    ])
