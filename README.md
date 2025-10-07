# 🧺 LaundryBot

LaundryBot is a Telegram bot that allows users to **manage laundry bookings** easily.  

I created this bot because in the student dormitory where I live in Trento, there is **no program to manage laundry reservations**. Every time someone wanted to book a washing machine or dryer, we had to manually write down who was using which machine.  

So I programmed this bot to **make the process simpler and automated**, allowing residents to book machines directly via Telegram.

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

