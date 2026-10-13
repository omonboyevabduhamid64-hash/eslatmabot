import sqlite3
from datetime import datetime
from config import DB_PATH, TIMEZONE

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Ma'lumotlar bazasini va jadvalni yaratish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                file_id TEXT,
                caption TEXT,
                remind_at TEXT NOT NULL,
                is_sent INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_remind_at ON reminders(remind_at, is_sent)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON reminders(user_id)")
        conn.commit()

def add_reminder(user_id: int, content_type: str, file_id: str | None, caption: str | None, remind_at: str) -> int:
    """Yangi eslatma qo'shish"""
    now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (user_id, content_type, file_id, caption, remind_at, is_sent, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (user_id, content_type, file_id, caption, remind_at, now_str))
        conn.commit()
        return cursor.lastrowid

def get_user_reminders(user_id: int, only_pending: bool = True):
    """Foydalanuvchining eslatmalarini olish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        if only_pending:
            cursor.execute("""
                SELECT * FROM reminders 
                WHERE user_id = ? AND is_sent = 0 
                ORDER BY remind_at ASC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT * FROM reminders 
                WHERE user_id = ? 
                ORDER BY remind_at DESC
                LIMIT 50
            """, (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_reminder_by_id(reminder_id: int, user_id: int | None = None):
    """Bitta eslatmani ID bo'yicha olish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
        else:
            cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_reminder(reminder_id: int, user_id: int) -> bool:
    """Eslatmani o'chirish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def update_reminder_time(reminder_id: int, user_id: int, new_remind_at: str) -> bool:
    """Eslatma vaqtini o'zgartirish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders 
            SET remind_at = ?, is_sent = 0 
            WHERE id = ? AND user_id = ?
        """, (new_remind_at, reminder_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def update_reminder_content(reminder_id: int, user_id: int, content_type: str, file_id: str | None, caption: str | None) -> bool:
    """Eslatma fayli yoki matnini o'zgartirish"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reminders 
            SET content_type = ?, file_id = ?, caption = ? 
            WHERE id = ? AND user_id = ?
        """, (content_type, file_id, caption, reminder_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

def get_due_reminders():
    """Muddati kelgan va hali yuborilmagan eslatmalarni olish"""
    now_str = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE remind_at <= ? AND is_sent = 0
            ORDER BY remind_at ASC
        """, (now_str,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def mark_as_sent(reminder_id: int):
    """Eslatmani yuborildi deb belgilash"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET is_sent = 1 WHERE id = ?", (reminder_id,))
        conn.commit()
