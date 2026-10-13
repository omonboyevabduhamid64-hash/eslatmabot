# ⏰ Telegram Eslatma Boti ("Esingizdami Hojayin")

Ushbu bot siz yuborgan har qanday **rasm**, **video**, **fayl/hujjat**, **ovozli xabar** yoki **matn**ni siz belgilagan sana va vaqtda sizga qayta yuboradi hamda **«Esingizdami Hojayin»** jumlasi bilan eslatadi.

---

## 🚀 Imkoniyatlar va Bosh panel

- ➕ **Yangi eslatma qo'shish**:
  - Rasm, video, fayl, audio, video xabar yoki oddiy matn qabul qiladi.
  - Tezkor tugmalar orqali sanani belgilash (Bugun, Ertaga, Indinga yoki qo'lda `15.10.2026`).
  - Vaqtni belgilash (15 daqiqadan so'ng, 1 soatdan so'ng, Ertalab 09:00 yoki qo'lda `14:30`).
  - Belgilangan daqiqada sizga fayl va **«Esingizdami Hojayin»** xabari yetib keladi.
- 📋 **Umumiy eslatmalar**:
  - Barcha faol va kutilayotgan eslatmalar ro'yxatini ko'rish.
  - Har bir eslatma ostida qulay inline tugmalar.
- ✏️ **Eslatmani o'zgartirish**:
  - Eslatma vaqtini (sana va soat) qayta belgilash.
  - Eslatma fayli yoki matnini yangisiga almashtirish.
- 🗑 **Eslatmani o'chirish**:
  - Ro'yxatdan kerakli eslatmani bitta bosish bilan o'chirib tashlash.

---

## 🛠 O'rnatish va Ishga tushirish

### 1. Telegram Bot Token olish:
1. Telegramda [@BotFather](https://t.me/botfather) ga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botingiz nomini va username-ni kiriting (masalan: `MeningEslatma_bot`).
4. BotFather sizga API Token beradi (masalan: `7123456789:AAEjK...`).

### 2. .env fayliga tokenni kiritish:
Loyihadagi `.env` faylini oching va tokenni yozing:
```env
BOT_TOKEN=7123456789:AAEjK_sizning_tokeningiz
```

### 3. Kutubxonalarni o'rnatish:
Agar hali o'rnatilmagan bo'lsa:
```bash
pip install -r requirements.txt
```

### 4. Botni ishga tushirish:
```bash
python main.py
```

---

## 📁 Loyiha tuzilishi

- `main.py` - Botning asosiy boshqaruv nuqtasi va Dispatcher
- `config.py` - Token va Toshkent vaqt mintaqasi (`Asia/Tashkent`) sozlamalari
- `database.py` - SQLite ma'lumotlar bazasi amallari (qo'shish, ko'rish, yangilash, o'chirish)
- `scheduler.py` - Orqa fonda har 5 soniyada eslatmalarni tekshirib, o'z vaqtida jo'natuvchi xizmat
- `keyboards.py` - Bosh panel, sana va vaqt tezkor klaviaturalari
- `states.py` - Aiogram FSM holatlari (AddReminder, EditReminder, DeleteReminder)
- `utils.py` - Sana va vaqtni tahlil qilish (parse) algoritmlari
- `handlers/` - Foydalanuvchi buyruqlari va xabarlarini qayta ishlovchi modullar:
  - `common.py` - `/start`, `/help` va bekor qilish
  - `add_reminder.py` - Yangi eslatma qo'shish
  - `list_reminders.py` - Barcha eslatmalarni ko'rish
  - `edit_reminder.py` - Eslatmani o'zgartirish
  - `delete_reminder.py` - Eslatmani o'chirish
