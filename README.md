# 🧺 LaundryBot

LaundryBot is a Telegram bot that allows users to **manage laundry bookings** easily.  

I created this bot because in the student dormitory where I live in Trento, there is **no program to manage laundry reservations**. Every time someone wanted to book a washing machine or dryer, we had to manually write down who was using which machine.  

So I programmed this bot to **make the process simpler and automated**, allowing residents to book machines directly via Telegram.

---




## 📸 Before & After

<table>
  <tr>
    <td align="center">
      <b>Before LaundryBot</b><br>
      <i>All bookings were done manually using many messages and notes</i>  <br>
    </td>
    <td align="center">
      <b>After LaundryBot</b><br>
      <i>Users book washing machines and dryers directly via Telegram </i>  <br>
    </td>
  </tr>  
      <td align="center">
      <img src="images/before.png" width="300">
      </td>
      <td align="center">
      <img src="images/after.png" width="300">
      </td>
</table>

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

## ⚙️ Installation (Win Terminal)
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












