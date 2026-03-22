"""Schedule management handler."""
import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from services.api_client import api
from keyboards.main_menu import schedule_menu, back_menu
from keyboards.schedule_kb import confirm_delete

WAITING_TIME = 1


async def schedule_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current schedule."""
    msg = update.callback_query.message if update.callback_query else update.message
    if update.callback_query:
        await update.callback_query.answer()

    sched = await api.get_schedule()
    times = []
    if sched:
        if isinstance(sched, list):
            times = [s.get('time', '') for s in sched if s.get('enabled', True)]
        elif isinstance(sched, dict):
            times = sched.get('times', sched.get('schedule', []))

    if not times:
        times = ['08:00', '14:00', '20:00']

    text = '📅 *Расписание кормлений*\n\n'
    for t in sorted(times):
        text += f'🕐 {t}\n'

    if update.callback_query:
        await msg.edit_text(text, parse_mode='Markdown', reply_markup=schedule_menu(sorted(times)))
    else:
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=schedule_menu(sorted(times)))


async def schedule_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    time = query.data.replace('sched_del_', '')
    await query.message.edit_text(
        f'Удалить кормление в *{time}*?',
        parse_mode='Markdown',
        reply_markup=confirm_delete(time)
    )


async def schedule_confirm_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    time = query.data.replace('sched_confirm_del_', '')

    sched = await api.get_schedule()
    times = []
    if sched:
        if isinstance(sched, list):
            times = [s.get('time', '') for s in sched if s.get('enabled', True)]
        elif isinstance(sched, dict):
            times = sched.get('times', sched.get('schedule', []))
    if not times:
        times = ['08:00', '14:00', '20:00']

    if time in times:
        times.remove(time)
    await api.update_schedule(times)
    await query.message.edit_text(f'✅ Кормление в {time} удалено', reply_markup=back_menu())


async def schedule_add_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        '⏰ Введите время кормления в формате *ЧЧ:ММ*\n(например: 12:30)',
        parse_mode='Markdown'
    )
    return WAITING_TIME


async def schedule_add_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not re.match(r'^\d{1,2}:\d{2}$', text):
        await update.message.reply_text('❌ Неверный формат. Введите время как ЧЧ:ММ')
        return WAITING_TIME

    h, m = text.split(':')
    time_str = f'{int(h):02d}:{int(m):02d}'

    sched = await api.get_schedule()
    times = []
    if sched:
        if isinstance(sched, list):
            times = [s.get('time', '') for s in sched if s.get('enabled', True)]
        elif isinstance(sched, dict):
            times = sched.get('times', sched.get('schedule', []))
    if not times:
        times = ['08:00', '14:00', '20:00']

    if time_str not in times:
        times.append(time_str)
        times.sort()
        await api.update_schedule(times)

    await update.message.reply_text(
        f'✅ Кормление в *{time_str}* добавлено',
        parse_mode='Markdown',
        reply_markup=back_menu()
    )
    return ConversationHandler.END


async def schedule_add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Отменено', reply_markup=back_menu())
    return ConversationHandler.END
