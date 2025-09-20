# db.py
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import List, Tuple

DB_PATH = "assistant.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            username TEXT,
            tz TEXT
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER,
            text TEXT,
            remind_at TEXT,        -- ISO datetime string in UTC
            repeat TEXT DEFAULT NULL, -- null | "daily" | "weekly:MON,TUE" etc
            active INTEGER DEFAULT 1,
            created_at TEXT
        );
        """)
        conn.commit()

def add_user(tg_id: int, username: str | None, tz: str | None):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (tg_id, username, tz) VALUES (?,?,?)",
            (tg_id, username, tz)
        )
        conn.commit()

def set_user_tz(tg_id: int, tz: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET tz=? WHERE tg_id=?", (tz, tg_id))
        conn.commit()

def add_reminder(tg_id: int, text: str, remind_at_iso_utc: str, repeat: str | None = None):
    created_at = datetime.utcnow().isoformat(sep=' ')
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reminders (tg_id, text, remind_at, repeat, created_at) VALUES (?,?,?,?,?)",
            (tg_id, text, remind_at_iso_utc, repeat, created_at)
        )
        conn.commit()
        return cur.lastrowid

def get_due_reminders(now_iso_utc: str) -> List[Tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, tg_id, text, remind_at, repeat FROM reminders WHERE active=1 AND remind_at<=?",
            (now_iso_utc,)
        )
        return cur.fetchall()

def mark_reminder_inactive(rem_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE reminders SET active=0 WHERE id=?", (rem_id,))
        conn.commit()

def update_reminder_next(rem_id: int, next_iso_utc: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE reminders SET remind_at=? WHERE id=?", (next_iso_utc, rem_id))
        conn.commit()
