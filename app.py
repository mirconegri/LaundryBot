# app.py
# LaundryBot - Telegram bot to manage laundry bookings with a conversational interface

import logging
import asyncio
import sys

# ---------------- CONFIGURATION CHECK ----------------
# The bot requires a 'config.py' file containing your BOT_TOKEN.
# If it's missing, the program exits with an error message.
try:
    import config
except ModuleNotFoundError:
    print("Error: config.py not found! Copy config.example.py to config.py and add your BOT_TOKEN.")
    sys.exit(1)

# ---------------- TELEGRAM IMPORTS ----------------
# Core classes and handlers from python-telegram-bot
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# ---------------- LOGGING ----------------
# Enables detailed logging for debugging and monitoring.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------- CONVERSATION STATES ----------------
# Each state represents a step in the user conversation.
CHOOSE_TYPE, CHOOSE_MACHINE, DURATION, EMPTY_MACHINE = range(4)

# ---------------- MACHINE DATA ----------------
# Lists of available machines.
washing_machines = ["A", "B", "C", "D", "E"]
dryers = ["1", "2", "3", "4"]

# Dictionary to store current bookings.
# Structure: {machine_name: {"user": username, "end_time": timestamp}}
bookings = {}

# ---------------- HELPER FUNCTION ----------------
def available_machines(machine_type):
    """
    Returns a list of available machines of a given type.
    machine_type: 'washing' or 'dryer'
    """
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

# ---------------- COMMAND HANDLERS ----------------

# /start — Entry point of the conversation.
# Asks the user whether they want to book a washing machine or a dryer.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Washing Machine")], [KeyboardButton("Dryer")]]
    await update.message.reply_text(
        "Welcome! Do you want to book a washing machine or a dryer?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_TYPE

# Step 1: Handle machine type choice (washing machine or dryer)
async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.lower()

    # Validate input
    if choice not in ["washing machine", "dryer"]:
        await update.message.reply_text("Please choose between Washing Machine or Dryer.")
        return CHOOSE_TYPE

    # Save the chosen type to user data
    context.user_data['type'] = "washing" if choice == "washing machine" else "dryer"

    # Get available machines of that type
    machines = available_machines(context.user_data['type'])

    # If all machines are booked, end the conversation
    if not machines:
        await update.message.reply_text(f"All {choice}s are currently booked.")
        return ConversationHandler.END

    # Otherwise, display available machines
    keyboard = [[KeyboardButton(m)] for m in machines]
    await update.message.reply_text(
        f"Choose which {choice} to book:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSE_MACHINE

# Step 2: Handle machine selection
async def choose_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    machine = update.message.text
    m_type = context.user_data['type']
    valid = washing_machines if m_type == "washing" else dryers

    # Validate machine name
    if machine not in valid:
        await update.message.reply_text("Invalid selection. Please choose again.")
        return CHOOSE_MACHINE

    # Save the selected machine to user data
    context.user_data['machine'] = machine
    await update.message.reply_text("For how long will you use it? (in minutes)")
    return DURATION

# Step 3: Handle booking duration
async def duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Validate that the duration is a positive integer
        minutes = int(update.message.text)
        if minutes <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a valid number of minutes.")
        return DURATION

    # Retrieve user and machine info
    machine = context.user_data['machine']
    user = update.message.from_user.username or update.message.from_user.first_name

    # Compute end time using asyncio's event loop clock
    end_time = asyncio.get_event_loop().time() + minutes * 60
    bookings[machine] = {"user": user, "end_time": end_time}

    # Confirm booking
    await update.message.reply_text(f"{machine} has been booked by {user} for {minutes} minutes.")

    # Schedule an automatic release of the machine when time expires
    asyncio.create_task(release_machine(machine, minutes))
    return ConversationHandler.END

# Helper function — Releases the machine automatically after the booking duration ends
async def release_machine(machine, minutes):
    await asyncio.sleep(minutes * 60)
    if machine in bookings:
        del bookings[machine]
        logging.info(f"{machine} released automatically after {minutes} minutes.")

# ---------------- EMPTY MACHINE COMMAND ----------------

# /empty — Allows users to manually free a machine
async def empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Empty")], [KeyboardButton("I emptied it")]]
    await update.message.reply_text(
        "Report the status of the machine:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return EMPTY_MACHINE

# Step for handling manual emptying
async def handle_empty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.lower()

    if choice in ["empty", "i emptied it"]:
        # If there are active bookings, remove the latest one
        if bookings:
            machine, _ = bookings.popitem()
            await update.message.reply_text(f"{machine} has been freed.")
        else:
            await update.message.reply_text("No machines are currently booked.")
    return ConversationHandler.END

# ---------------- CANCEL COMMAND ----------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# ---------------- MAIN FUNCTION ----------------
if __name__ == '__main__':
    import platform

    # Fix for Windows asyncio compatibility issues
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Create the main bot application
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # Define the conversation flow
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

    # Add the conversation handler to the bot
    app.add_handler(conv_handler)

    # Start the bot
    print("🤖 LaundryBot is running...")
    app.run_polling()