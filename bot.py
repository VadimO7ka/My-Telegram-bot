# bot.py
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from dateutil import parser
import requests

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes,
)

# импорт твоих модулей (предполагаю, они есть по-прежнему)
from db import init_db, get_due_reminders, mark_reminder_inactive, update_reminder_next
from handlers.commands import start, help_command, set_tz_command
from handlers.callback_handlers import callback_router
from handlers.reminders import text_handler

# load .env
load_dotenv()
TOKEN = os.getenv("TG_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

if not TOKEN:
    raise ValueError("Ошибка: TG_TOKEN не найден. Проверь .env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def job_check_reminders(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(sep=' ')
    try:
        due = get_due_reminders(now)  # ожидает список (id, tg_id, text, remind_at, repeat)
    except Exception:
        logger.exception("Ошибка при выборке напоминаний из БД")
        return

    for rid, tg_id, text, remind_at, repeat in due:
        try:
            await context.bot.send_message(chat_id=tg_id, text=f"🔔 Напоминание: {text}")
            if repeat:
                if repeat == "daily":
                    dt = parser.parse(remind_at)
                    next_dt = dt + timedelta(days=1)
                    update_reminder_next(rid, next_dt.astimezone(timezone.utc).isoformat(sep=' '))
                else:
                    mark_reminder_inactive(rid)
            else:
                mark_reminder_inactive(rid)
        except Exception:
            logger.exception("Не удалось отправить напоминание id=%s пользователю %s", rid, tg_id)


def delete_webhook_sync(token: str):
    """Удаляем webhook синхронно через HTTP, чтобы не ждать await."""
    try:
        url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        # параметр drop_pending_updates можно передать в JSON или как параметр
        resp = requests.post(url, json={"drop_pending_updates": True}, timeout=10)
        if resp.ok:
            logger.info("Webhook очищен (sync HTTP).")
        else:
            logger.warning("Ответ при удалении webhook: %s %s", resp.status_code, resp.text)
    except Exception:
        logger.exception("Не удалось синхронно удалить webhook (но продолжаю).")

def main():
    # Удаляем возможный webhook до создания Application (синхронно)
    delete_webhook_sync(TOKEN)

    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settz", set_tz_command))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    # background job
    app.job_queue.run_repeating(job_check_reminders, interval=CHECK_INTERVAL, first=10)

    logger.info("Запускаю бота — app.run_polling() (Ctrl+C для остановки)...")
    # Запуск polling (блокирующий) — библиотека сама управляет event loop
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Завершение работы (Ctrl+C).")
    except Exception:
        logger.exception("Неожиданная ошибка в основном цикле.")
