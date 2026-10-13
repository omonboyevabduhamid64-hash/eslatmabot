from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from datetime import datetime, timedelta
from config import TIMEZONE

def get_main_menu() -> ReplyKeyboardMarkup:
    """Asosiy bosh panel tugmalari"""
    keyboard = [
        [
            KeyboardButton(text="➕ Yangi eslatma qo'shish"),
            KeyboardButton(text="📋 Umumiy eslatmalar")
        ],
        [
            KeyboardButton(text="✏️ Eslatmani o'zgartirish"),
            KeyboardButton(text="🗑 Eslatmani o'chirish")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi"""
    keyboard = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_quick_dates() -> ReplyKeyboardMarkup:
    """Tezkor sanani tanlash tugmalari"""
    now = datetime.now(TIMEZONE)
    today = now.strftime("%d.%m.%Y")
    tomorrow = (now + timedelta(days=1)).strftime("%d.%m.%Y")
    after_tomorrow = (now + timedelta(days=2)).strftime("%d.%m.%Y")

    keyboard = [
        [KeyboardButton(text=f"📅 Bugun ({today})")],
        [KeyboardButton(text=f"📅 Ertaga ({tomorrow})")],
        [KeyboardButton(text=f"📅 Indinga ({after_tomorrow})")],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_quick_times() -> ReplyKeyboardMarkup:
    """Tezkor vaqtni tanlash tugmalari"""
    keyboard = [
        [
            KeyboardButton(text="⏱ 15 daqiqadan so'ng"),
            KeyboardButton(text="⏱ 30 daqiqadan so'ng")
        ],
        [
            KeyboardButton(text="⏱ 1 soatdan so'ng"),
            KeyboardButton(text="⏱ 3 soatdan so'ng")
        ],
        [
            KeyboardButton(text="⏰ Ertalab 09:00"),
            KeyboardButton(text="⏰ Tushlik 14:00"),
            KeyboardButton(text="⏰ Kechqurun 20:00")
        ],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_reminder_action_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    """Har bir eslatma ostidagi inline tugmalar"""
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ O'zgartirish", callback_data=f"edit:{reminder_id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del:{reminder_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_edit_options_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    """Eslatmani nimasini o'zgartirishni tanlash"""
    keyboard = [
        [
            InlineKeyboardButton(text="🕒 Vaqtini o'zgartirish", callback_data=f"edit_time:{reminder_id}"),
            InlineKeyboardButton(text="📁 Fayl/Matnini o'zgartirish", callback_data=f"edit_content:{reminder_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel_edit")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
