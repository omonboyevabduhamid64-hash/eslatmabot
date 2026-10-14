import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import os
from aiohttp import web

from config import BOT_TOKEN
from database import init_db
from scheduler import reminder_scheduler_loop
from handlers import (
    common,
    add_reminder,
    list_reminders,
    edit_reminder,
    delete_reminder,
    group_reminder
)

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def start_web_server():
    """Bulutli serverlar (Render, Koyeb) uchun portni ochish"""
    port_str = os.getenv("PORT")
    if not port_str:
        return
    try:
        port = int(port_str)
        app = web.Application()
        app.router.add_get("/", lambda r: web.Response(text="Bot is running!"))
        app.router.add_get("/health", lambda r: web.Response(text="OK"))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Bulutli veb-server {port}-portda faollashtirildi.")
    except Exception as e:
        logger.warning(f"Veb-serverni ishga tushirishda xatolik (mahalliy rejimda zararsiz): {e}")

async def main():
    if not BOT_TOKEN:
        logger.error(
            "⚠️ DIQQAT: BOT_TOKEN aniqlanmadi!\n"
            "Iltimos, '.env' fayliga Telegram botingiz tokenini yozing:\n"
            "BOT_TOKEN=sizning_bot_tokeningiz"
        )
        sys.exit(1)

    # Ma'lumotlar bazasini tayyorlash
    init_db()
    logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")

    # Agar bulutli hostingda bo'lsa, portni ochish
    await start_web_server()

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Handler routerlarini ro'yxatdan o'tkazish
    dp.include_router(group_reminder.router)
    dp.include_router(common.router)
    dp.include_router(add_reminder.router)
    dp.include_router(list_reminders.router)
    dp.include_router(edit_reminder.router)
    dp.include_router(delete_reminder.router)

    # Orqa fonda eslatmalarni tekshirib turuvchi fon jarayonini boshlash
    asyncio.create_task(reminder_scheduler_loop(bot))

    logger.info("Bot ishga tushdi va xabarlarni qabul qilmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
