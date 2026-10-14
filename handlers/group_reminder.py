from aiogram import Router, F
from aiogram.types import Message
from database import add_reminder
from utils import parse_group_datetime

router = Router()

# Faqat guruh va superguruh xabarlari uchun
router.message.filter(F.chat.type.in_({"group", "supergroup"}))

@router.message(F.text.regexp(r"^/(eslat|eslatma|remind)", flags=2) | F.caption.regexp(r"^/(eslat|eslatma|remind)", flags=2))
async def handle_group_reminder_command(message: Message):
    """
    Guruhda /eslat komandasi orqali eslatma qo'shish.
    Qo'llab-quvvatlaydi:
    1. Xabarga javob (reply) qilib: /eslat 18:00
    2. Rasm/video bilan birga: /eslat ertaga 10:00
    3. Oddiy matn bilan: /eslat 15 daqiqa Majlis bor
    """
    raw_text = message.text or message.caption or ""
    remind_at, clean_caption, error = parse_group_datetime(raw_text)

    if error:
        await message.reply(
            f"{error}\n\n"
            "💡 <b>Qo'llash namunalari:</b>\n"
            "• <code>/eslat 18:30</code> (bugun soat 18:30 da)\n"
            "• <code>/eslat ertaga 09:00</code>\n"
            "• <code>/eslat 30 daqiqa</code>\n"
            "• <code>/eslat 16.10.2026 14:00</code>\n"
            "<i>(Istalgan rasm yoki videoga javob (reply) qilib ham yozishingiz mumkin)</i>",
            parse_mode="HTML"
        )
        return

    # Eslatma ob'ektini aniqlash (agar xabarga reply qilingan bo'lsa, o'sha xabarni olamiz)
    target_msg = message.reply_to_message if message.reply_to_message else message

    content_type = "text"
    file_id = None
    caption = clean_caption or target_msg.caption or ""

    if target_msg.photo:
        content_type = "photo"
        file_id = target_msg.photo[-1].file_id
    elif target_msg.video:
        content_type = "video"
        file_id = target_msg.video.file_id
    elif target_msg.document:
        content_type = "document"
        file_id = target_msg.document.file_id
    elif target_msg.audio:
        content_type = "audio"
        file_id = target_msg.audio.file_id
    elif target_msg.voice:
        content_type = "voice"
        file_id = target_msg.voice.file_id
    elif target_msg.video_note:
        content_type = "video_note"
        file_id = target_msg.video_note.file_id
    elif target_msg.text:
        content_type = "text"
        caption = clean_caption or target_msg.text
        # Agar reply bo'lsa va komandada alohida izoh yozilgan bo'lsa
        if message.reply_to_message and clean_caption:
            caption = f"{clean_caption}\n(Asl xabar: {target_msg.text})"

    # MUHIM: user_id bu komandani bergan odam (Hojayin), eslatma uning lichkasiga boradi!
    user_id = message.from_user.id
    reminder_id = add_reminder(
        user_id=user_id,
        content_type=content_type,
        file_id=file_id,
        caption=caption,
        remind_at=remind_at
    )

    types_uz = {
        "photo": "🖼 Rasm",
        "video": "🎥 Video",
        "document": "📁 Hujjat/Fayl",
        "audio": "🎵 Audio",
        "voice": "🎤 Ovozli xabar",
        "video_note": "🔘 Video xabar",
        "text": "📝 Matn"
    }
    t_name = types_uz.get(content_type, "Xabar")

    response_text = (
        f"✅ <b>Eslatma qabul qilindi, {message.from_user.first_name}!</b>\n\n"
        f"🆔 Eslatma raqami: <b>#{reminder_id}</b>\n"
        f"📌 Turi: <b>{t_name}</b>\n"
        f"⏰ Eslatish vaqti: <code>{remind_at}</code>\n\n"
        f"🔒 <i>Belgilangan vaqtda bu eslatma guruhga emas, aynan sizning <b>shaxsiy lichkangizga</b> yetkaziladi.</i>"
    )

    await message.reply(response_text, parse_mode="HTML")
