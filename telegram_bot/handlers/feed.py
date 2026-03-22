"""Feed handler."""
from telegram import Update
from telegram.ext import ContextTypes
from services.api_client import api
from keyboards.main_menu import feed_portions, back_menu


async def feed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /feed command. Optional argument: portion in grams."""
    if context.args:
        try:
            portion = int(context.args[0])
            portion = max(10, min(100, portion))
            await _do_feed(update, portion)
            return
        except ValueError:
            pass

    msg = update.message or update.callback_query.message
    if update.callback_query:
        await update.callback_query.answer()
        await msg.edit_text('🍽 *Выберите порцию:*', parse_mode='Markdown', reply_markup=feed_portions())
    else:
        await msg.reply_text('🍽 *Выберите порцию:*', parse_mode='Markdown', reply_markup=feed_portions())


async def feed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle feed_XX callbacks."""
    query = update.callback_query
    await query.answer()
    portion = int(query.data.split('_')[1])
    await _do_feed(update, portion)


async def _do_feed(update: Update, portion: int):
    msg = update.callback_query.message if update.callback_query else update.message
    result = await api.trigger_feed(portion)
    if result and result.get('success'):
        text = f'✅ Кормление запущено: *{portion}г*'
    else:
        text = '❌ Не удалось запустить кормление'

    if update.callback_query:
        await msg.edit_text(text, parse_mode='Markdown', reply_markup=back_menu())
    else:
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=back_menu())
