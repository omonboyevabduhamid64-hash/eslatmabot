import asyncio
import logging
from aiogram import Bot
from database import get_due_reminders, mark_as_sent

logger = logging.getLogger(__name__)

async def send_reminder(bot: Bot, reminder: dict):
    """Muddati kelgan bitta eslatmani foydalanuvchiga jo'natish"""
    user_id = reminder["user_id"]
    content_type = reminder["content_type"]
    file_id = reminder["file_id"]
    caption = reminder["caption"] or ""

    header = "🔔 <b>Esingizdami Hojayin?</b>"
    full_text = f"{header}\n\n{caption}".strip()

    try:
        if content_type == "photo":
            await bot.send_photo(chat_id=user_id, photo=file_id, caption=full_text, parse_mode="HTML")
        elif content_type == "video":
            await bot.send_video(chat_id=user_id, video=file_id, caption=full_text, parse_mode="HTML")
        elif content_type == "document":
            await bot.send_document(chat_id=user_id, document=file_id, caption=full_text, parse_mode="HTML")
        elif content_type == "audio":
            await bot.send_audio(chat_id=user_id, audio=file_id, caption=full_text, parse_mode="HTML")
        elif content_type == "voice":
            await bot.send_voice(chat_id=user_id, voice=file_id, caption=full_text, parse_mode="HTML")
        elif content_type == "video_note":
            await bot.send_video_note(chat_id=user_id, video_note=file_id)
            await bot.send_message(chat_id=user_id, text=full_text, parse_mode="HTML")
        elif content_type == "text":
            await bot.send_message(chat_id=user_id, text=full_text, parse_mode="HTML")
        else:
            await bot.send_message(chat_id=user_id, text=full_text, parse_mode="HTML")

        logger.info(f"Eslatma #{reminder['id']} foydalanuvchi {user_id} ga muvaffaqiyatli yetkazildi.")
    except Exception as e:
        logger.error(f"Eslatma #{reminder['id']} yuborishda xatolik yuz berdi: {e}")
    finally:
        # Har qanday holatda ham qayta-qayta yuborilmasligi uchun belgilanadi
        mark_as_sent(reminder["id"])

async def reminder_scheduler_loop(bot: Bot):
    """Orqa fonda har 5 soniyada eslatmalarni tekshirib turuvchi fon jarayoni"""
    logger.info("Eslatmalar tekshiruvchi fon xizmati ishga tushdi.")
    while True:
        try:
            due_reminders = get_due_reminders()
            for rem in due_reminders:
                await send_reminder(bot, rem)
        except Exception as e:
            logger.error(f"Scheduler siklida xatolik: {e}")

        await asyncio.sleep(5)
