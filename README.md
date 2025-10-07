# 🧺 LaundryBot

LaundryBot is a Telegram bot that allows users to **manage laundry bookings** easily.  

I created this bot because in the student dormitory where I live in Trento, there is **no program to manage laundry reservations**. Every time someone wanted to book a washing machine or dryer, we had to manually write down who was using which machine.  

So I programmed this bot to **make the process simpler and automated**, allowing residents to book machines directly via Telegram.

---

<table>
  <tr>
    <td align="center">
      <b>Before LaundryBot</b><br>
    </td>
    <td align="center">
      <b>After LaundryBot</b><br>
    </td>
  </tr>  
      <td align="center">
      <img src="images/before.png" width="300">
      </td>
      <td align="center">
      <img src="images/after.png" width="300">
      </td>
</table>


## 📸 Before & After

**Before LaundryBot**  
_Manual booking with paper notes and group messages_  
<img src="images/before.png" width="300" />

**After LaundryBot**  
_Users book washing machines and dryers directly via Telegram_  
<img src="images/after.png" width="300" />

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
Copy the example config:
cp config.example.py config.py
Edit config.py and add your Telegram bot token.
Run the bot:
python app.py





