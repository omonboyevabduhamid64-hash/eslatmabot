from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import AddReminder
from keyboards import get_main_menu, get_cancel_keyboard, get_quick_dates, get_quick_times
from utils import parse_date_input, parse_time_input
from database import add_reminder

router = Router()

@router.message(F.text == "➕ Yangi eslatma qo'shish")
async def start_add_reminder(message: Message, state: FSMContext):
    """Yangi eslatma yaratishni boshlash"""
    await state.clear()
    await state.set_state(AddReminder.waiting_for_content)
    await message.answer(
        "📥 <b>Eslatma uchun fayl yoki xabar yuboring:</b>\n\n"
        "Siz quyidagilardan birini yuborishingiz mumkin:\n"
        "• 🖼 Rasm (rasm tagida izoh ham yozishingiz mumkin)\n"
        "• 🎥 Video\n"
        "• 📁 Hujjat / Fayl\n"
        "• 🎵 Audio yoki Ovozli xabar\n"
        "• 📝 Oddiy matnli xabar\n\n"
        "<i>Eslatma vaqti kelganda, bot aynan shu ma'lumotni sizga jo'natadi.</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AddReminder.waiting_for_content)
async def process_content(message: Message, state: FSMContext):
    """Yuborilgan fayl yoki matnni qabul qilish"""
    content_type = None
    file_id = None
    caption = message.caption or ""

    if message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id
    elif message.document:
        content_type = "document"
        file_id = message.document.file_id
    elif message.audio:
        content_type = "audio"
        file_id = message.audio.file_id
    elif message.voice:
        content_type = "voice"
        file_id = message.voice.file_id
    elif message.video_note:
        content_type = "video_note"
        file_id = message.video_note.file_id
    elif message.text:
        content_type = "text"
        caption = message.text
    else:
        await message.answer(
            "⚠️ Noma'lum format. Iltimos rasm, video, fayl yoki matn yuboring.",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(
        content_type=content_type,
        file_id=file_id,
        caption=caption
    )

    await state.set_state(AddReminder.waiting_for_date)
    await message.answer(
        "📅 <b>Qaysi sanada eslatish kerak?</b>\n\n"
        "Quyidagi tayyor tugmalardan birini bosing yoki sanani "
        "<code>KK.OO.YYYY</code> (masalan: <code>15.10.2026</code>) formatida yozing:",
        reply_markup=get_quick_dates(),
        parse_mode="HTML"
    )

@router.message(AddReminder.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    """Sanani tekshirish va qabul qilish"""
    date_str = parse_date_input(message.text)
    if not date_str:
        await message.answer(
            "⚠️ Sana tushunarsiz bo'ldi.\n"
            "Iltimos, pastdagi tugmalardan tanlang yoki <code>KK.OO.YYYY</code> (masalan: <code>15.10.2026</code>) shaklida kiriting.",
            reply_markup=get_quick_dates(),
            parse_mode="HTML"
        )
        return

    await state.update_data(selected_date=date_str)
    await state.set_state(AddReminder.waiting_for_time)
    await message.answer(
        f"⏰ <b>Sana tanlandi:</b> <code>{date_str}</code>\n\n"
        "Endi soat nechida eslatish kerakligini belgilang:\n"
        "Tezkor tugmalardan foydalaning yoki vaqtni <code>SS:DD</code> (masalan: <code>14:30</code>) formatida yozing:",
        reply_markup=get_quick_times(),
        parse_mode="HTML"
    )

@router.message(AddReminder.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    """Vaqtni tekshirish va eslatmani bazaga saqlash"""
    data = await state.get_data()
    selected_date = data.get("selected_date")

    remind_at, error = parse_time_input(message.text, selected_date)
    if error or not remind_at:
        await message.answer(
            error or "⚠️ Vaqt noto'g'ri kiritildi. Qaytadan urinib ko'ring (masalan: <code>18:00</code>):",
            reply_markup=get_quick_times(),
            parse_mode="HTML"
        )
        return

    # Bazaga yozish
    reminder_id = add_reminder(
        user_id=message.from_user.id,
        content_type=data["content_type"],
        file_id=data["file_id"],
        caption=data["caption"],
        remind_at=remind_at
    )

    types_uz = {
        "photo": "🖼 Rasm",
        "video": "🎥 Video",
        "document": "📁 Hujjat/Fayl",
        "audio": "🎵 Audio",
        "voice": "🎤 Ovozli xabar",
        "video_note": "🔘 Dumaloq video",
        "text": "📝 Matn"
    }
    t_name = types_uz.get(data["content_type"], "Fayl")

    success_msg = (
        "✅ <b>Eslatma muvaffaqiyatli saqlandi!</b>\n\n"
        f"🆔 Eslatma raqami: <b>#{reminder_id}</b>\n"
        f"📌 Turi: <b>{t_name}</b>\n"
        f"⏰ Eslatish vaqti: <code>{remind_at}</code>\n\n"
        "<i>Belgilangan vaqtda bot sizga ushbu faylni «Esingizdami Hojayin» deb yetkazadi.</i>"
    )

    await state.clear()
    await message.answer(success_msg, reply_markup=get_main_menu(), parse_mode="HTML")
