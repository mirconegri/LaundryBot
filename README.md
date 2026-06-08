# 🧺 LaundryBot

[![](https://img.shields.io/badge/Language-python-blue?style=for-the-badge)](https://www.python.org/) [![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

LaundryBot is a Telegram bot that allows users to **manage laundry bookings** easily.

I created this bot because in the student dormitory where I live in Trento, there is **no system to manage laundry reservations**. Every time someone wanted to book a washing machine or dryer, we had to manually write down who was using which machine.

So I built this bot to **make the process simpler and automated**, allowing residents to book machines directly via Telegram.

---

<h2 align="center"> 📸 Before & After </h2>

<table align="center">
  <tr>
    <td align="center">
      <b>Before LaundryBot</b><br>
      <i>All bookings were done manually using messages and notes</i>
    </td>
    <td align="center">
      <b>After LaundryBot</b><br>
      <i>Users book washing machines and dryers directly via Telegram</i>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="images/before.png" width="300">
    </td>
    <td align="center">
      <img src="images/after.png" width="300">
    </td>
  </tr>
</table>

---

## 🚀 Features

- ✅ `Book` a washing machine or dryer through a guided conversation
- 📋 `View` all active bookings with remaining time
- 🗑️ `Free` a machine manually before the timer expires
- ⏱️ `Auto-release` machines automatically when the booking expires
- 💾 `Persist` bookings to a local JSON file (survives restarts)

---

## 🛠️ Technologies

- `Python 3.10+`
- `python-telegram-bot 21.x` (async, PTB v20+ API)
- `Flask` (optional — for webhook or web dashboard integration)
- `JSON` for local data storage

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```
git clone https://github.com/mirconegri/LaundryBot.git
cd LaundryBot
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows:** `venv\Scripts\activate`
- **macOS / Linux:** `source venv/bin/activate`

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Create your bot on Telegram

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the token you receive (e.g. `7312456789:AAF...`)

### 5️⃣ Configure the bot

```
cp config.example.py config.py      # macOS / Linux
copy config.example.py config.py    # Windows
```

Open `config.py` and paste your token:

```python
BOT_TOKEN = "your_token_here"
```

### 6️⃣ Run the bot

```
python app.py
```

You should see `🤖 LaundryBot is running...` in the terminal.  
Open Telegram, search for your bot by name, and start with `/start`.

> The bot uses **long polling** — no server, open ports, or external hosting needed for local testing. It works as long as the terminal is open.

---

## 🧾 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start a new booking (guided conversation) |
| `/view` | Show all active bookings with remaining time |
| `/free` | Manually free a machine before the timer expires |
| `/cancel` | Cancel the current operation (during a conversation) |
| `/help` | Show the list of available commands |

---

## 📁 Project Structure

```
LaundryBot/
├── app.py              # Main bot logic
├── config.py           # Your bot token (not committed)
├── config.example.py   # Template for config.py
├── requirements.txt    # Python dependencies
├── data/
│   └── bookings.json   # Active bookings (auto-generated, not committed)
└── images/
    ├── before.png
    └── after.png
```

---

## 👤 Author & Connect

**Mirco Negri** — *Computer Science Student @ UniTrento*

[![Portfolio](https://img.shields.io/badge/Portfolio-00599C?style=for-the-badge&logo=globe&logoColor=white)](https://mirconegri.com)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mirconegri)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mirco-negri-263810225)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:mirconegri06@gmail.com)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/mirco_negri_?igsh=MWtlbXY0a3R4NTJmNA==)
[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/share/172rhaPCUK/)

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.  
© 2026 Mirco Negri
