"""Statistics handler with chart generation."""
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from services.api_client import api
from services.chart_generator import generate_food_level_chart, generate_feedings_chart
from keyboards.main_menu import stats_periods, back_menu


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()

    text = '📈 *Статистика*\nВыберите период:'
    if update.callback_query:
        await msg.edit_text(text, parse_mode='Markdown', reply_markup=stats_periods())
    else:
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=stats_periods())


async def stats_period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer('Генерирую графики...')

    period = query.data.replace('stats_', '')
    period_map = {'day': '24h', 'week': '7d', 'month': '30d'}
    period_label = {'day': 'день', 'week': 'неделю', 'month': 'месяц'}

    stats = await api.get_stats(period)
    telemetry = await api.get_telemetry(period_map.get(period, '24h'), 200)

    charts = []

    if telemetry:
        buf = generate_food_level_chart(telemetry)
        charts.append(InputMediaPhoto(buf, caption=f'📊 Уровни за {period_label.get(period, period)}'))

    if stats:
        buf = generate_feedings_chart(stats)
        caption = '' if charts else f'📊 Статистика за {period_label.get(period, period)}'
        charts.append(InputMediaPhoto(buf, caption=caption))

    if charts:
        await query.message.reply_media_group(charts)
        await query.message.reply_text('Выберите другой период:', reply_markup=stats_periods())
    else:
        await query.message.edit_text(
            '📈 Нет данных за этот период',
            reply_markup=back_menu()
        )
