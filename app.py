# app.py
# LaundryBot - Telegram bot to manage laundry bookings with a conversational interface

import logging
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta

# ---------------- CONFIGURATION CHECK ----------------
try:
    import config
except ModuleNotFoundError:
    print("Error: config.py not found! Copy config.example.py to config.py and add your BOT_TOKEN.")
    sys.exit(1)

# ---------------- TELEGRAM IMPORTS ----------------
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# ---------------- LOGGING ----------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- CONVERSATION STATES ----------------
# Booking flow states
CHOOSE_TYPE, CHOOSE_MACHINE, DURATION = range(3)
# Empty/free flow state (separate namespace to avoid conflicts)
EMPTY_CHOOSE_MACHINE = 3

# ---------------- MACHINE DATA ----------------
washing_machines = ["A", "B", "C", "D", "E"]
dryers = ["1", "2", "3", "4"]

# Bookings dictionary.
# Structure: {machine_name: {"user": username, "end_time": iso_string, "minutes": int}}
bookings = {}

# ---------------- PERSISTENCE ----------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")


def load_bookings():
    """Load bookings from JSON file, discarding expired ones."""
    global bookings
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BOOKINGS_FILE):
        bookings = {}
        return
    try:
        with open(BOOKINGS_FILE, "r") as f:
            raw = json.load(f)
        now = datetime.utcnow()
        # Filter out expired bookings
        bookings = {
            machine: data
            for machine, data in raw.items()
            if datetime.fromisoformat(data["end_time"]) > now
        }
        logger.info(f"Loaded {len(bookings)} active booking(s) from disk.")
    except (json.JSONDecodeError, KeyError, ValueError):
        logger.warning("Could not parse bookings.json, starting fresh.")
        bookings = {}


def save_bookings():
    """Persist current bookings to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=2)


# ---------------- HELPER FUNCTIONS ----------------

def available_machines(machine_type: str) -> list[str]:
    """Return machines of the given type that are not currently booked."""
    pool = washing_machines if machine_type == "washing" else dryers
    return [m for m in pool if m not in bookings]


def booked_machines(machine_type: str) -> list[str]:
    """Return machines of the given type that are currently booked."""
    pool = washing_machines if machine_type == "washing" else dryers
    return [m for m in pool if m in bookings]


def format_booking_list() -> str:
    """Return a human-readable summary of all active bookings."""
    if not bookings:
        return "Nessuna prenotazione attiva. ✅"
    lines = ["📋 *Prenotazioni attive:*\n"]
    for machine, data in bookings.items():
        end_dt = datetime.fromisoformat(data["end_time"])
        # Show remaining minutes
        remaining = max(0, int((end_dt - datetime.utcnow()).total_seconds() / 60))
        label = "🫧 Lavatrice" if machine in washing_machines else "🌀 Asciugatrice"
        lines.append(
            f"{label} *{machine}* — {data['user']} — ancora ~{remaining} min"
        )
    return "\n".join(lines)


# ---------------- COMMAND: /start (booking flow) ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: ask the user whether they want to book a washer or dryer."""
    keyboard = [[KeyboardButton("🫧 Lavatrice"), KeyboardButton("🌀 Asciugatrice")]]
    await update.message.reply_text(
        "👋 Benvenuto su *LaundryBot*!\n\nCosa vuoi prenotare?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CHOOSE_TYPE


async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle machine-type choice."""
    text = update.message.text.strip()

    if "lavatrice" in text.lower():
        machine_type = "washing"
        label = "lavatrice"
    elif "asciugatrice" in text.lower():
        machine_type = "dryer"
        label = "asciugatrice"
    else:
        await update.message.reply_text("Per favore scegli *Lavatrice* o *Asciugatrice*.", parse_mode="Markdown")
        return CHOOSE_TYPE

    context.user_data["type"] = machine_type

    machines = available_machines(machine_type)
    if not machines:
        await update.message.reply_text(
            f"😕 Tutte le {label}e sono attualmente occupate.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    keyboard = [[KeyboardButton(m)] for m in machines]
    await update.message.reply_text(
        f"Quale {label} vuoi prenotare?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CHOOSE_MACHINE


async def choose_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle specific machine selection."""
    machine = update.message.text.strip()
    m_type = context.user_data.get("type", "washing")
    valid = washing_machines if m_type == "washing" else dryers

    if machine not in valid:
        await update.message.reply_text("⚠️ Selezione non valida. Riprova.")
        return CHOOSE_MACHINE

    if machine in bookings:
        await update.message.reply_text(
            f"⚠️ La macchina *{machine}* è già prenotata. Scegline un'altra.",
            parse_mode="Markdown",
        )
        return CHOOSE_MACHINE

    context.user_data["machine"] = machine
    await update.message.reply_text(
        "⏱ Per quanti minuti la userai?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return DURATION


async def duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle booking duration and confirm."""
    try:
        minutes = int(update.message.text.strip())
        if minutes <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Inserisci un numero intero positivo di minuti.")
        return DURATION

    machine = context.user_data["machine"]
    user = update.message.from_user.username or update.message.from_user.first_name

    end_time = datetime.utcnow() + timedelta(minutes=minutes)
    bookings[machine] = {
        "user": user,
        "end_time": end_time.isoformat(),
        "minutes": minutes,
    }
    save_bookings()

    await update.message.reply_text(
        f"✅ *{machine}* prenotata da *{user}* per *{minutes}* minuti.\n"
        f"Libera alle {(datetime.now() + timedelta(minutes=minutes)).strftime('%H:%M')} circa.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Schedule automatic release
    asyncio.create_task(release_machine(machine, minutes))
    return ConversationHandler.END


async def release_machine(machine: str, minutes: int):
    """Release a machine automatically after its booking expires."""
    await asyncio.sleep(minutes * 60)
    if machine in bookings:
        del bookings[machine]
        save_bookings()
        logger.info(f"Machine {machine} released automatically after {minutes} minutes.")


# ---------------- COMMAND: /view ----------------

async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all active bookings."""
    await update.message.reply_text(
        format_booking_list(),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )


# ---------------- COMMAND: /cancel (inside conversation) ----------------

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current operation."""
    await update.message.reply_text(
        "❌ Operazione annullata.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ---------------- COMMAND: /free — manually free a specific machine ----------------

async def free_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask which booked machine to free."""
    all_booked = [m for m in bookings]
    if not all_booked:
        await update.message.reply_text(
            "ℹ️ Non ci sono macchine prenotate al momento.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    keyboard = [[KeyboardButton(m)] for m in all_booked]
    await update.message.reply_text(
        "🗑 Quale macchina vuoi liberare?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return EMPTY_CHOOSE_MACHINE


async def free_choose_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Free the chosen machine."""
    machine = update.message.text.strip()
    if machine not in bookings:
        await update.message.reply_text(
            f"⚠️ *{machine}* non risulta prenotata.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    booked_by = bookings[machine]["user"]
    del bookings[machine]
    save_bookings()

    await update.message.reply_text(
        f"✅ Macchina *{machine}* liberata (era prenotata da {booked_by}).",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ---------------- COMMAND: /help ----------------

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    text = (
        "🤖 *LaundryBot — Comandi disponibili*\n\n"
        "/start — Prenota una lavatrice o asciugatrice\n"
        "/view — Visualizza le prenotazioni attive\n"
        "/free — Libera manualmente una macchina\n"
        "/cancel — Annulla l'operazione corrente\n"
        "/help — Mostra questo messaggio\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ---------------- MAIN ----------------

if __name__ == "__main__":
    import platform

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Load persisted bookings on startup
    load_bookings()

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # --- Booking conversation ---
    booking_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_type)],
            CHOOSE_MACHINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_machine)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, duration)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # --- Free/empty conversation ---
    free_handler = ConversationHandler(
        entry_points=[CommandHandler("free", free_start)],
        states={
            EMPTY_CHOOSE_MACHINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, free_choose_machine)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(booking_handler)
    app.add_handler(free_handler)
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 LaundryBot is running...")
    app.run_polling()
