# app.py
# Minimal LaundryBot skeleton using python-telegram-bot v21+
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import config  # local config.py with BOT_TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm LaundryBot 👕. Use /book to book a laundry slot (demo)."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Available commands: /start /help /book /cancel")

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Demo: simple booking confirmation (replace with real booking logic)
    user = update.effective_user
    await update.message.reply_text(f"Thanks {user.first_name}, your laundry booking is registered (demo).")

def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("book", book))

    print("Starting LaundryBot (polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()
