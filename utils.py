import re
from datetime import datetime, timedelta
from config import TIMEZONE

def parse_date_input(text: str) -> str | None:
    """
    Kiritilgan matndan sanani aniqlash (YYYY-MM-DD formatida qaytaradi).
    Qo'llab-quvvatlaydi:
    - 'Bugun', 'Ertaga', 'Indinga'
    - '14.10.2026', '14/10/2026', '14-10-2026'
    - '2026-10-14'
    """
    text = text.strip()
    now = datetime.now(TIMEZONE)

    if "bugun" in text.lower():
        return now.strftime("%Y-%m-%d")
    elif "ertaga" in text.lower():
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "indinga" in text.lower():
        return (now + timedelta(days=2)).strftime("%Y-%m-%d")

    # Qavs ichidagi sana (masalan: "📅 Bugun (14.10.2026)")
    match_bracket = re.search(r"\((\d{1,2}\.\d{1,2}\.\d{4})\)", text)
    if match_bracket:
        try:
            dt = datetime.strptime(match_bracket.group(1), "%d.%m.%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY
    match_dmy = re.search(r"^(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})$", text)
    if match_dmy:
        day, month, year = int(match_dmy.group(1)), int(match_dmy.group(2)), int(match_dmy.group(3))
        try:
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # YYYY-MM-DD
    match_ymd = re.search(r"^(\d{4})[./\-](\d{1,2})[./\-](\d{1,2})$", text)
    if match_ymd:
        year, month, day = int(match_ymd.group(1)), int(match_ymd.group(2)), int(match_ymd.group(3))
        try:
            dt = datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    return None

def parse_time_input(text: str, selected_date_str: str) -> tuple[str | None, str | None]:
    """
    Kiritilgan matndan vaqtni aniqlash.
    Qaytaradi: (to'liq_sana_vaqt_str, xatolik_matni)
    to'liq_sana_vaqt_str formati: YYYY-MM-DD HH:MM:SS
    """
    text = text.strip()
    now = datetime.now(TIMEZONE)

    # Tezkor nisbiy vaqtlar (15 daqiqa, 30 daqiqa, 1 soat, 3 soat)
    if "15 daqiqa" in text.lower():
        target = now + timedelta(minutes=15)
        return target.strftime("%Y-%m-%d %H:%M:00"), None
    elif "30 daqiqa" in text.lower():
        target = now + timedelta(minutes=30)
        return target.strftime("%Y-%m-%d %H:%M:00"), None
    elif "1 soat" in text.lower():
        target = now + timedelta(hours=1)
        return target.strftime("%Y-%m-%d %H:%M:00"), None
    elif "3 soat" in text.lower():
        target = now + timedelta(hours=3)
        return target.strftime("%Y-%m-%d %H:%M:00"), None

    # Ertalab 09:00, Tushlik 14:00, Kechqurun 20:00 kabi tugmalar
    match_quick_time = re.search(r"(\d{1,2}):(\d{2})", text)
    if match_quick_time:
        hour, minute = int(match_quick_time.group(1)), int(match_quick_time.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            try:
                date_part = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
                target_dt = datetime(
                    date_part.year, date_part.month, date_part.day,
                    hour, minute, 0, tzinfo=TIMEZONE
                )

                if target_dt <= now:
                    return None, "⚠️ Belgilangan vaqt o'tib ketgan! Iltimos, kelgusi vaqtni kiriting."

                return target_dt.strftime("%Y-%m-%d %H:%M:%S"), None
            except Exception as e:
                return None, f"⚠️ Sana yoki vaqtda xatolik: {e}"

    return None, "⚠️ Vaqt formati noto'g'ri! Iltimos, masalan <code>14:30</code> yoki <code>09:00</code> formatida kiriting."

def format_reminder_summary(reminder: dict) -> str:
    """Eslatmani chiroyli matn sifatida ko'rsatish"""
    types_uz = {
        "photo": "🖼 Rasm",
        "video": "🎥 Video",
        "document": "📁 Hujjat/Fayl",
        "audio": "🎵 Audio",
        "voice": "🎤 Ovozli xabar",
        "text": "📝 Matn"
    }
    c_type = types_uz.get(reminder["content_type"], "Noma'lum")
    caption = reminder["caption"] or "<i>Izohsiz</i>"
    remind_at = reminder["remind_at"]

    return (
        f"🆔 <b>Eslatma #{reminder['id']}</b>\n"
        f"📌 <b>Turi:</b> {c_type}\n"
        f"⏰ <b>Eslatish vaqti:</b> <code>{remind_at}</code>\n"
        f"📝 <b>Izoh / Matn:</b> {caption}\n"
    )
