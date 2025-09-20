# handlers/callback_handlers.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import get_due_reminders, mark_reminder_inactive

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "create_reminder":
        await query.message.reply_text("Отправь напоминание в формате:\n`YYYY-MM-DD HH:MM | Текст` или просто `через 2 часа | Текст`", parse_mode="Markdown")
        context.user_data['awaiting_reminder'] = True
    elif data == "list_reminders":
        # простая реализация: показать ближайшие активные (можно дописать функцию выборки)
        await query.message.reply_text("Список напоминаний (пока упрощённо).")
    elif data.startswith("cancel:"):
        rid = int(data.split(":",1)[1])
        mark_reminder_inactive(rid)
        await query.message.reply_text("Напоминание отменено.")
