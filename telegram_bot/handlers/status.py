"""Status handler."""
from telegram import Update
from telegram.ext import ContextTypes
from services.api_client import api
from keyboards.main_menu import back_menu


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.callback_query.message
    if update.callback_query:
        await update.callback_query.answer()

    s = await api.get_status()
    if not s:
        await msg.reply_text('❌ Не удалось получить статус устройства', reply_markup=back_menu())
        return

    food = s.get('foodLevel', s.get('food_level', 0))
    water = s.get('waterLevel', s.get('water_level', 0))
    battery = s.get('batteryLevel', s.get('battery_level', 0))
    temp = s.get('temperature', 0)
    wifi = s.get('wifiSignal', s.get('wifi_signal', 0))
    motor = s.get('motorStatus', s.get('motor_status', 'idle'))
    cat = s.get('catDetected', s.get('cat_detected', False))
    bowl = s.get('weightBowl', s.get('weight_bowl', 0))
    feedings = s.get('totalFeedingsToday', s.get('total_feedings_today', 0))
    door = s.get('doorOpen', s.get('door_open', False))

    food_bar = _bar(food)
    water_bar = _bar(water)
    battery_bar = _bar(battery)

    motor_icons = {'idle': '⚪', 'running': '🟢', 'error': '🔴'}
    motor_labels = {'idle': 'Простой', 'running': 'Работает', 'error': 'ОШИБКА'}

    text = f"""📊 *Статус кормушки*

🍽 Корм: {food_bar} {food:.0f}%
💧 Вода: {water_bar} {water:.0f}%
🔋 Батарея: {battery_bar} {battery:.0f}%

🌡 Температура: {temp:.1f}°C
📶 WiFi: {wifi} dBm
{motor_icons.get(motor, '⚪')} Мотор: {motor_labels.get(motor, motor)}
🐱 Кот: {'обнаружен' if cat else 'нет'}
⚖ Миска: {bowl:.1f}г
🚪 Дверца: {'открыта' if door else 'закрыта'}
🍽 Кормлений сегодня: {feedings}"""

    if update.callback_query:
        await msg.edit_text(text, parse_mode='Markdown', reply_markup=back_menu())
    else:
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=back_menu())


def _bar(pct: float) -> str:
    filled = int(pct / 10)
    return '█' * filled + '░' * (10 - filled)
