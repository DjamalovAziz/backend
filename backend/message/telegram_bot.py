# backend\message\telegram_bot.py:

import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from django.conf import settings
from django.contrib.auth import get_user_model

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~

User = get_user_model()
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm your password reset bot. "
        f"Your chat ID is: {update.effective_chat.id}"
    )

    # Log the user's chat ID
    logger.info(
        f"User {user.username} (ID: {user.id}) started the bot. Chat ID: {update.effective_chat.id}"
    )


async def bind_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bind Telegram account to user account."""
    message_text = update.message.text.strip()
    parts = message_text.split()

    if len(parts) != 2:
        await update.message.reply_text(
            "Please provide your email address: /bind youremail@example.com"
        )
        return

    email = parts[1]
    chat_id = update.effective_chat.id

    try:
        user = User.objects.get(email=email)
        user.telegram_chat_id = str(chat_id)
        user.telegram_username = update.effective_user.username
        user.save()

        await update.message.reply_text(
            f"Your account has been successfully bound to {email}"
        )
        logger.info(f"User {email} bound to Telegram chat ID: {chat_id}")
    except User.DoesNotExist:
        await update.message.reply_text("No account found with that email address.")
        logger.warning(f"Failed binding attempt for email: {email}, chat ID: {chat_id}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /start - Start the bot and get your chat ID
    /bind email@example.com - Bind your Telegram account to your user account
    /help - Show this help message
    """
    await update.message.reply_text(help_text)


def run_bot():
    """Run the bot."""
    # Create the Application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("bind", bind_account))

    # Run the bot
    application.run_polling()


def start_bot_in_thread():
    """Start the bot in a separate thread."""
    import threading

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
