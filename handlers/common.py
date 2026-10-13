from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasi - asosiy panelni ochish"""
    await state.clear()
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        "🤖 <b>Eslatma botiga xush kelibsiz!</b>\n\n"
        "Men siz yuborgan har qanday rasm, video, hujjat/fayl yoki matnni belgilangan vaqtda:\n"
        "<i>«Esingizdami Hojayin»</i> jumlasi bilan yuborib eslatib turaman.\n\n"
        "Boshqarish uchun quyidagi menyudan foydalaning:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(), parse_mode="HTML")

@router.message(F.text == "❌ Bekor qilish")
async def cmd_cancel(message: Message, state: FSMContext):
    """Amalni bekor qilish"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Hech qanday jarayon faol emas.", reply_markup=get_main_menu())
        return

    await state.clear()
    await message.answer("❌ Jarayon bekor qilindi. Bosh panel:", reply_markup=get_main_menu())

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam komandasi"""
    help_text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma:</b>\n\n"
        "1. <b>➕ Yangi eslatma qo'shish</b> - istalgan rasm, video, fayl yoki matn yuborasiz, so'ng sana va soatni tanlaysiz.\n"
        "2. <b>📋 Umumiy eslatmalar</b> - barcha kutilayotgan eslatmalaringiz ro'yxatini ko'rish.\n"
        "3. <b>✏️ Eslatmani o'zgartirish</b> - vaqtni yoki eslatma faylini tahrirlash.\n"
        "4. <b>🗑 Eslatmani o'chirish</b> - keraksiz eslatmani o'chirib tashlash.\n\n"
        "Belgilangan daqiqada bot sizga o'sha faylni <b>«Esingizdami Hojayin»</b> deb yuboradi!"
    )
    await message.answer(help_text, reply_markup=get_main_menu(), parse_mode="HTML")
