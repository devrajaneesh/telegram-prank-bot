import os
import asyncio
from threading import Thread

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# -----------------------------
# Settings
# -----------------------------

TOKEN = os.getenv("BOT_TOKEN")

NAME, PARTNER = range(2)

# -----------------------------
# Small web server for Render
# -----------------------------

app = Flask(__name__)


@app.route("/")
def home():
    return "Telegram Prank Bot is running! 😂"


def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


# -----------------------------
# Telegram Bot
# -----------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔮 Start Prediction", callback_data="start_prediction")]
    ]

    await update.message.reply_text(
        "🔮 *Know Your & Your Partner's Future* 🔮\n\n"
        "_According to Numerology & Astrology_\n\n"
        "✨ Discover what destiny has planned for your relationship...",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def start_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "👤 Enter your name:"
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "❤️ Enter your partner's name:"
    )

    return PARTNER


async def get_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    partner_name = update.message.text
    context.user_data["partner"] = partner_name

    messages = [
        "🔮 Analyzing astrology...",
        "🔢 Calculating numerology...",
        "🌌 Checking planetary alignment...",
        "⚡ Destiny calculation in progress...",
    ]

    for message in messages:
        await update.message.reply_text(message)
        await asyncio.sleep(1)

    await update.message.reply_text(
        "🚨 *PREDICTION COMPLETE* 🚨\n\n"
        f"❤️ Partner: *{partner_name}*\n\n"
        "🔮 *Prediction:*\n\n"
        f'💥 Tumhari wife "{partner_name}" Rajaneesh ke saath bhaag jayegi 😂😂\n\n'
        "⚠️ _Just for fun — this is a prank, not a real prediction._",
        parse_mode="Markdown",
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Try Again", callback_data="start_prediction")]
    ]

    await update.message.reply_text(
        "😂 Want to check again?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Prediction cancelled.\n\n"
        "Use /start to try again."
    )

    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_prediction":
        await query.message.reply_text(
            "👤 Enter your name:"
        )

        return NAME


# -----------------------------
# Start everything
# -----------------------------

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing.")

    # Start Render web server
    Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                button_handler,
                pattern="^start_prediction$"
            )
        ],
        states={
            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name
                )
            ],
            PARTNER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_partner
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        per_user=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conversation)

    print("Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
