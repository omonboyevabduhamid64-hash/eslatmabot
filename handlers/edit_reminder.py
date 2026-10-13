from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import EditReminder
from database import get_reminder_by_id, get_user_reminders, update_reminder_time, update_reminder_content
from keyboards import get_main_menu, get_cancel_keyboard, get_quick_dates, get_quick_times, get_edit_options_keyboard
from utils import parse_date_input, parse_time_input, format_reminder_summary

router = Router()

@router.callback_query(F.data.startswith("edit:"))
async def inline_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Inline tugma orqali tahrirlash menyusini ochish"""
    reminder_id = int(callback.data.split(":")[1])
    rem = get_reminder_by_id(reminder_id, callback.from_user.id)

    if not rem:
        await callback.answer("⚠️ Eslatma topilmadi.", show_alert=True)
        return

    await state.clear()
    await state.update_data(editing_reminder_id=reminder_id)
    await state.set_state(EditReminder.waiting_for_action)

    await callback.message.answer(
        f"✏️ <b>Eslatma #{reminder_id} tahrirlash</b>\n\n"
        f"{format_reminder_summary(rem)}\n"
        "Nimani o'zgartirmoqchisiz?",
        reply_markup=get_edit_options_keyboard(reminder_id),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(F.text == "✏️ Eslatmani o'zgartirish")
async def start_edit_from_menu(message: Message, state: FSMContext):
    """Menyudan tahrirlashni tanlash"""
    await state.clear()
    reminders = get_user_reminders(message.from_user.id, only_pending=True)

    if not reminders:
        await message.answer(
            "📭 O'zgartirish uchun faol eslatmalar mavjud emas.",
            reply_markup=get_main_menu()
        )
        return

    buttons = []
    for r in reminders:
        type_symbol = {
            "photo": "🖼", "video": "🎥", "document": "📁",
            "audio": "🎵", "voice": "🎤", "text": "📝"
        }.get(r["content_type"], "📌")
        btn_text = f"✏️ #{r['id']} {type_symbol} ({r['remind_at']})"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"edit:{r['id']}")])

    buttons.append([InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel_edit")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "✏️ <b>Qaysi eslatmani o'zgartirmoqchisiz?</b>\n"
        "O'zgartirmoqchi bo'lgan eslatmangiz ustiga bosing yoki uning ID raqamini yozing:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(EditReminder.waiting_for_id)

@router.callback_query(F.data == "cancel_edit")
async def cancel_edit_callback(callback: CallbackQuery, state: FSMContext):
    """Tahrirlashni bekor qilish"""
    await state.clear()
    await callback.message.edit_text("❌ Tahrirlash bekor qilindi.")
    await callback.message.answer("Bosh panel:", reply_markup=get_main_menu())

@router.message(EditReminder.waiting_for_id)
async def process_edit_by_id(message: Message, state: FSMContext):
    """ID raqam yozib tanlanganda"""
    text = message.text.replace("#", "").strip()
    if not text.isdigit():
        await message.answer("⚠️ Iltimos faqat eslatma ID raqamini kiriting (masalan: <code>5</code>):", parse_mode="HTML")
        return

    rem_id = int(text)
    rem = get_reminder_by_id(rem_id, message.from_user.id)
    if not rem:
        await message.answer("⚠️ Bunday eslatma topilmadi yoki u sizga tegishli emas.", reply_markup=get_main_menu())
        await state.clear()
        return

    await state.update_data(editing_reminder_id=rem_id)
    await state.set_state(EditReminder.waiting_for_action)

    await message.answer(
        f"✏️ <b>Eslatma #{rem_id} tahrirlash</b>\n\n"
        f"{format_reminder_summary(rem)}\n"
        "Nimani o'zgartirmoqchisiz?",
        reply_markup=get_edit_options_keyboard(rem_id),
        parse_mode="HTML"
    )

# --- Vaqtni o'zgartirish qismi ---
@router.callback_query(F.data.startswith("edit_time:"))
async def edit_time_callback(callback: CallbackQuery, state: FSMContext):
    """Yangi sanani so'rash"""
    reminder_id = int(callback.data.split(":")[1])
    await state.update_data(editing_reminder_id=reminder_id)
    await state.set_state(EditReminder.waiting_new_date)

    await callback.message.answer(
        "📅 <b>Yangi sanani tanlang yoki kiriting:</b>\n"
        "Quyidagi tugmalardan birini bosing yoki <code>KK.OO.YYYY</code> shaklida yozing:",
        reply_markup=get_quick_dates(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(EditReminder.waiting_new_date)
async def process_new_date(message: Message, state: FSMContext):
    """Yangi sanani qabul qilish"""
    date_str = parse_date_input(message.text)
    if not date_str:
        await message.answer(
            "⚠️ Sana tushunarsiz. Iltimos tugmalardan birini bosing yoki <code>KK.OO.YYYY</code> (masalan: <code>15.10.2026</code>) shaklida kiriting.",
            reply_markup=get_quick_dates(),
            parse_mode="HTML"
        )
        return

    await state.update_data(new_date=date_str)
    await state.set_state(EditReminder.waiting_new_time)
    await message.answer(
        f"⏰ <b>Yangi sana tanlandi:</b> <code>{date_str}</code>\n\n"
        "Endi yangi soatni tanlang yoki <code>SS:DD</code> (masalan: <code>14:30</code>) formatida yozing:",
        reply_markup=get_quick_times(),
        parse_mode="HTML"
    )

@router.message(EditReminder.waiting_new_time)
async def process_new_time(message: Message, state: FSMContext):
    """Yangi vaqtni qabul qilish va bazani yangilash"""
    data = await state.get_data()
    reminder_id = data["editing_reminder_id"]
    new_date = data["new_date"]

    remind_at, error = parse_time_input(message.text, new_date)
    if error or not remind_at:
        await message.answer(
            error or "⚠️ Vaqt noto'g'ri kiritildi. Qaytadan urinib ko'ring:",
            reply_markup=get_quick_times(),
            parse_mode="HTML"
        )
        return

    update_reminder_time(reminder_id, message.from_user.id, remind_at)
    await state.clear()
    await message.answer(
        f"✅ <b>Eslatma #{reminder_id} vaqti muvaffaqiyatli yangilandi!</b>\n"
        f"⏰ Yangi vaqt: <code>{remind_at}</code>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

# --- Fayl/Matnni o'zgartirish qismi ---
@router.callback_query(F.data.startswith("edit_content:"))
async def edit_content_callback(callback: CallbackQuery, state: FSMContext):
    """Yangi fayl yoki matnni so'rash"""
    reminder_id = int(callback.data.split(":")[1])
    await state.update_data(editing_reminder_id=reminder_id)
    await state.set_state(EditReminder.waiting_new_content)

    await callback.message.answer(
        "📥 <b>Yangi rasm, video, fayl yoki matn yuboring:</b>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(EditReminder.waiting_new_content)
async def process_new_content(message: Message, state: FSMContext):
    """Yangi fayl yoki matnni qabul qilish va bazada almashtirish"""
    data = await state.get_data()
    reminder_id = data["editing_reminder_id"]

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

    update_reminder_content(reminder_id, message.from_user.id, content_type, file_id, caption)
    await state.clear()
    await message.answer(
        f"✅ <b>Eslatma #{reminder_id} mazmuni muvaffaqiyatli yangilandi!</b>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
