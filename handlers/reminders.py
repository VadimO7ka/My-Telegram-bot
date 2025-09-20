# handlers/reminders.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import parse_user_datetime
from db import add_reminder, get_due_reminders, update_reminder_next
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    if context.user_data.get('awaiting_reminder'):
        # ожидаем формат "datetime | text" или "через 2 часа | текст"
        try:
            when_part, message_part = text.split("|", 1)
            when_part = when_part.strip()
            message_part = message_part.strip()
            # парсим дату с учётом user tz, если указан
            user_tz = context.user_data.get('tz') or None
            dt_utc = parse_user_datetime(when_part, user_tz)
            iso_utc = dt_utc.isoformat(sep=' ')
            rid = add_reminder(user.id, message_part, iso_utc, repeat=None)
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("Отменить", callback_data=f"cancel:{rid}")]])
            await update.message.reply_text(f"Напоминание создано на {iso_utc} UTC.", reply_markup=kb)
            context.user_data['awaiting_reminder'] = False
        except Exception as e:
            await update.message.reply_text("Не удалось понять формат. Используй `YYYY-MM-DD HH:MM | Текст` или 'через 2 часа | Текст'.", parse_mode="Markdown")
    else:
        # базовая обработка — позволим пользователю напрямую присылать "напомни: через 10 минут сделать Х"
        if text.lower().startswith("напомни") or "|" in text:
            # попытаемся создать напоминание прямо
            try:
                if "|" in text:
                    when_part, message_part = text.split("|", 1)
                else:
                    # для случая "напомни через 10 минут сделать что-то"
                    parts = text.split(" ", 2)
                    if len(parts) < 3:
                        raise ValueError("Недостаточно частей в сообщении")
                    when_part = parts[1]  # "через 10 минут"
                    message_part = parts[2]  # "сделать что-то"
                user_tz = context.user_data.get('tz') or None
                dt_utc = parse_user_datetime(when_part, user_tz)
                iso_utc = dt_utc.isoformat(sep=' ')
                rid = add_reminder(user.id, message_part.strip(), iso_utc, repeat=None)
                kb = InlineKeyboardMarkup([[InlineKeyboardButton("Отменить", callback_data=f"cancel:{rid}")]])
                await update.message.reply_text(f"Напоминание создано на {iso_utc} UTC.", reply_markup=kb)
            except Exception:
                await update.message.reply_text("Не понял. Для создания напоминания используй: `YYYY-MM-DD HH:MM | Текст`", parse_mode="Markdown")
        else:
            await update.message.reply_text("Не понимаю. Нажми /help или кнопку 'Создать напоминание'.")
