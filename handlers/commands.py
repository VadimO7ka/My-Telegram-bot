# handlers/commands.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import add_user, set_user_tz
import os

DEFAULT_TZ = os.getenv("DEFAULT_TZ", "Asia/Almaty")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, DEFAULT_TZ)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Создать напоминание", callback_data="create_reminder")],
        [InlineKeyboardButton("Мои напоминания", callback_data="list_reminders")],
        [InlineKeyboardButton("Настройки", callback_data="settings")]
    ])
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я — твой персональный ассистент.\n"
        "Нажми кнопку, чтобы начать.",
        reply_markup=kb
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — запустить бота\n/help — помощь\n"
        "Чтобы создать напоминание — нажми кнопку 'Создать напоминание' или отправь в чат:\n"
        "`2025-09-20 18:00 | Купить хлеб`",
        parse_mode="Markdown"
    )

async def set_tz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /settz Asia/Almaty
    user = update.effective_user
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /settz Asia/Almaty")
        return
    tz = args[0]
    set_user_tz(user.id, tz)
    await update.message.reply_text(f"Часовой пояс сохранён: {tz}")
