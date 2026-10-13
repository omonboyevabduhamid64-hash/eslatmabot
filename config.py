import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Vaqt mintaqasi (O'zbekiston)
TIMEZONE = ZoneInfo("Asia/Tashkent")

# Ma'lumotlar bazasi fayli
DB_PATH = os.path.join(os.path.dirname(__file__), "reminders.db")
