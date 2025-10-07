# 🧺 LaundryBot

LaundryBot is a Telegram bot designed to manage **laundry bookings** automatically.  
Users can view available slots, book a laundry slot, and cancel their bookings directly via Telegram.

---

## 🚀 Features
- 📅 View available time slots
- ✅ Book a laundry slot
- 🗑️ Cancel or update a booking
- 💾 Store data locally using JSON

---

## 🛠️ Technologies
- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Flask (optional web integration)
- JSON for local data storage

---

## ⚙️ Installation
```bash
git clone https://github.com/mirconegri/LaundryBot.git
cd LaundryBot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
