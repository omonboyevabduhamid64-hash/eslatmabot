from aiogram import Router, F
from aiogram.types import Message
from database import get_user_reminders
from utils import format_reminder_summary
from keyboards import get_main_menu, get_reminder_action_keyboard

router = Router()

@router.message(F.text.in_(["📋 Umumiy eslatmalar", "📋 Barcha eslatmalar"]))
async def list_reminders_handler(message: Message):
    """Foydalanuvchining barcha faol eslatmalarini ko'rsatish"""
    reminders = get_user_reminders(message.from_user.id, only_pending=True)

    if not reminders:
        await message.answer(
            "📭 <b>Sizda hozircha faol eslatmalar yo'q.</b>\n\n"
            "Yangi eslatma yaratish uchun <b>➕ Yangi eslatma qo'shish</b> tugmasini bosing.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        return

    await message.answer(
        f"📋 <b>Sizning faol eslatmalaringiz (Jami: {len(reminders)} ta):</b>\n"
        "Quyidagi ro'yxatdan har bir eslatmani o'zgartirishingiz yoki o'chirishingiz mumkin:",
        parse_mode="HTML"
    )

    for rem in reminders:
        text = format_reminder_summary(rem)
        keyboard = get_reminder_action_keyboard(rem["id"])
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
