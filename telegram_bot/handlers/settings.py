"""Settings handler."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from services.api_client import api
from keyboards.settings_kb import settings_menu
from keyboards.main_menu import back_menu

WAITING_VALUE = 1
_pending_setting: dict = {}


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()

    s = await api.get_settings()
    if not s:
        s = {}

    pet = s.get('petName', s.get('pet_name', '—'))
    food_type = s.get('foodType', s.get('food_type', '—'))
    pet_weight = s.get('petWeight', s.get('pet_weight', '—'))
    food_thr = s.get('lowFoodThreshold', s.get('low_food_threshold', 20))
    water_thr = s.get('lowWaterThreshold', s.get('low_water_threshold', 20))

    text = f"""⚙️ *Настройки*

🐱 Питомец: {pet}
🍖 Тип корма: {food_type}
⚖ Вес питомца: {pet_weight} кг
🔔 Порог корма: {food_thr}%
💧 Порог воды: {water_thr}%"""

    if update.callback_query:
        await msg.edit_text(text, parse_mode='Markdown', reply_markup=settings_menu())
    else:
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=settings_menu())


SETTING_MAP = {
    'set_petname': ('petName', '🐱 Введите имя питомца:'),
    'set_foodtype': ('🍖 Введите тип корма:', 'foodType'),
    'set_petweight': ('petWeight', '⚖ Введите вес питомца (кг):'),
    'set_food_threshold': ('lowFoodThreshold', '🔔 Введите порог корма (%):'),
    'set_water_threshold': ('lowWaterThreshold', '💧 Введите порог воды (%):'),
}


async def setting_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    prompts = {
        'set_petname': ('petName', '🐱 Введите имя питомца:'),
        'set_foodtype': ('foodType', '🍖 Введите тип корма:'),
        'set_petweight': ('petWeight', '⚖ Введите вес питомца (кг):'),
        'set_food_threshold': ('lowFoodThreshold', '🔔 Введите порог корма (%):'),
        'set_water_threshold': ('lowWaterThreshold', '💧 Введите порог воды (%):'),
    }

    if action in prompts:
        key, prompt = prompts[action]
        context.user_data['pending_setting'] = key
        await query.message.edit_text(prompt)
        return WAITING_VALUE

    return ConversationHandler.END


async def setting_value_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get('pending_setting')
    if not key:
        await update.message.reply_text('Ошибка', reply_markup=back_menu())
        return ConversationHandler.END

    value = update.message.text.strip()

    # Convert numeric values
    if key in ('petWeight', 'lowFoodThreshold', 'lowWaterThreshold'):
        try:
            value = float(value)
        except ValueError:
            await update.message.reply_text('❌ Введите число')
            return WAITING_VALUE

    await api.update_settings({key: value})
    await update.message.reply_text(f'✅ Настройка обновлена', reply_markup=back_menu())
    context.user_data.pop('pending_setting', None)
    return ConversationHandler.END


async def setting_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('pending_setting', None)
    await update.message.reply_text('Отменено', reply_markup=back_menu())
    return ConversationHandler.END
