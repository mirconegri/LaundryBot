# app.py
# LaundryBot - Telegram bot to manage laundry bookings with conversation
import logging
import asyncio
import sys

# Check config.py
try:
    import config
except ModuleNotFoundError:
    print("Error: config.py not found! Copy config.example.py to config.py and add your BOT_TOKEN.")
    sys.exit(1)

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# ---------------- Logging ----------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------- Conversation states ----------------
CHOOSE_TYPE, CHOOSE_MACHINE, DURATION, EMPTY_MACHINE = range(4)

# ---------------- Initial availability ----------------
washing_machines = ["A", "B", "C", "D", "E"]
dryers = ["1", "2", "3", "4"]
bookings = {}  # {machine: {"user": username, "end_time": timestamp}}

# ---------------- Helper functions ----------------
def available_machines(machine_type):
    available = []
    if machine_type == "washing":
        for m in washing_machines:
            if m not in bookings:
                available.append(m)
    else:
        for d in dryers:
            if d not in bookings:
                available.append(d)
    return available

# ---------------- Command handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Washing Machine")], [KeyboardButton("Dryer")]]
    await update.message.reply_text(
        "Welcome! Do you want to book a washing machine or a dryer?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_TYPE

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.lower()
    if choice not in ["washing machine", "dryer"]:
        await update.message.reply_text("Please choose between Washing Machine or Dryer")
        return CHOOSE_TYPE
    context.user_data['type'] = "washing" if choice == "washing machine" else "dryer"
    machines = available_machines(context.user_data['type'])
    if not machines:
        await update.message.reply_text(f"All {choice}s are currently booked.")
        return ConversationHandler.END
    keyboard = [[KeyboardButton(m)] for m in machines]
    await update.message.reply_text(
        f"Choose which {choice} to book:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_MACHINE

async def choose_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    machine = update.message.text
    m_type = context.user_data['type']
    valid = washing_machines if m_type == "washing" else dryers
    if machine not in valid:
        await update.message.reply_text("Invalid selection.")
        return CHOOSE_MACHINE
    context.user_data['machine'] = machine
    await update.message.reply_text("For how long will you use it? (minutes)")
    return DURATION

async def duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        minutes = int(update.message.text)
        if minutes <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a valid number of minutes.")
        return DURATION

    machine = context.user_data['machine']
    user = update.message.from_user.username or update.message.from_user.first_name
    end_time = asyncio.get_event_loop().time() + minutes*60
    bookings[machine] = {"user": user, "end_time": end_time}

    await update.message.reply_text(f"{machine} booked by {user} for {minutes} minutes.")

    # Schedule automatic release
    asyncio.create_task(release_machine(machine, minutes))
    return ConversationHandler.END

async def release_machine(machine, minutes):
    await asyncio.sleep(minutes*60)
    if machine in bookings:
        del bookings[machine]
        logging.info(f"{machine} released automatically.")

# /empty command
async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Empty")], [KeyboardButton("I emptied it")]]
    await update.message.reply_text(
        "Report the status of the machine:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return EMPTY_MACHINE

async def handle_empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.lower()
    if choice in ["empty", "i emptied it"]:
        if bookings:
            machine, _ = bookings.popitem()
            await update.message.reply_text(f"{machine} has been freed.")
        else:
            await update.message.reply_text("No machines to empty.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# ---------------- Main ----------------
if __name__ == '__main__':
    import platform

    # Fix for Windows asyncio
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    from telegram.ext import ConversationHandler

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('empty', empty)],
        states={
            CHOOSE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_type)],
            CHOOSE_MACHINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_machine)],
            DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, duration)],
            EMPTY_MACHINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_empty)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)

    print("🤖 LaundryBot is running...")
    app.run_polling()
