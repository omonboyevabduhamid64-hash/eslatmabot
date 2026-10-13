from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import DeleteReminder
from database import delete_reminder, get_user_reminders, get_reminder_by_id
from keyboards import get_main_menu, get_cancel_keyboard

router = Router()

@router.callback_query(F.data.startswith("del:"))
async def inline_delete_callback(callback: CallbackQuery):
    """Inline tugma orqali o'chirish"""
    reminder_id = int(callback.data.split(":")[1])
    success = delete_reminder(reminder_id, callback.from_user.id)

    if success:
        await callback.answer("✅ Eslatma o'chirildi!", show_alert=True)
        await callback.message.edit_text(
            f"🗑 <b>Eslatma #{reminder_id} o'chirildi.</b>",
            parse_mode="HTML"
        )
    else:
        await callback.answer("⚠️ Eslatma topilmadi yoki allaqachon o'chirilgan.", show_alert=True)

@router.message(F.text == "🗑 Eslatmani o'chirish")
async def start_delete_from_menu(message: Message, state: FSMContext):
    """Menyudan o'chirishni tanlash"""
    await state.clear()
    reminders = get_user_reminders(message.from_user.id, only_pending=True)

    if not reminders:
        await message.answer(
            "📭 O'chirish uchun faol eslatmalar mavjud emas.",
            reply_markup=get_main_menu()
        )
        return

    # Eslatmalarni inline tugma qilib chiqarish
    buttons = []
    for r in reminders:
        type_symbol = {
            "photo": "🖼", "video": "🎥", "document": "📁",
            "audio": "🎵", "voice": "🎤", "text": "📝"
        }.get(r["content_type"], "📌")
        btn_text = f"🗑 #{r['id']} {type_symbol} ({r['remind_at']})"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"del:{r['id']}")])

    buttons.append([InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel_del")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        "🗑 <b>Qaysi eslatmani o'chirmoqchisiz?</b>\n"
        "O'chirmoqchi bo'lgan eslatmangiz ustiga bosing yoki uning ID raqamini yozing:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(DeleteReminder.waiting_for_id)

@router.callback_query(F.data == "cancel_del")
async def cancel_del_callback(callback: CallbackQuery, state: FSMContext):
    """O'chirishni bekor qilish"""
    await state.clear()
    await callback.message.edit_text("❌ O'chirish bekor qilindi.")
    await callback.message.answer("Bosh panel:", reply_markup=get_main_menu())

@router.message(DeleteReminder.waiting_for_id)
async def process_delete_by_id(message: Message, state: FSMContext):
    """Foydalanuvchi ID raqam yozib yuborganda o'chirish"""
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

    delete_reminder(rem_id, message.from_user.id)
    await state.clear()
    await message.answer(f"✅ <b>Eslatma #{rem_id} muvaffaqiyatli o'chirildi!</b>", reply_markup=get_main_menu(), parse_mode="HTML")
