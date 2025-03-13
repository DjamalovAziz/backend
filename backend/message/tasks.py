# backend\message\tasks.py:

import logging
import requests
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client

logger = logging.getLogger(__name__)

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~


def send_reset_code(user, code, delivery_method):
    """
    Send reset code to user via the specified delivery method
    """
    if delivery_method == "telegram":
        return send_telegram_code(user, code)
    elif delivery_method == "sms":
        return send_sms_code(user, code)
    elif delivery_method == "email":
        return send_email_code(user, code)
    else:
        raise ValueError(f"Unsupported delivery method: {delivery_method}")


def send_telegram_code(user, code):
    """
    Send reset code via Telegram bot
    """
    if not user.telegram_chat_id:
        raise ValueError("User does not have a telegram_chat_id")

    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = user.telegram_chat_id

    message = f"Your password reset code is: {code}\nIt will expire in 10 minutes."

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    response = requests.post(url, data=data)
    if not response.ok:
        logger.error(f"Failed to send Telegram message: {response.text}")
        raise Exception(f"Telegram API error: {response.text}")

    return True


def send_sms_code(user, code):
    """
    Send reset code via SMS using Twilio
    """
    if not user.phone_number:
        raise ValueError("User does not have a phone number")

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = f"Your password reset code is: {code}. It will expire in 10 minutes."

    try:
        client.messages.create(
            body=message, from_=settings.TWILIO_PHONE_NUMBER, to=user.phone_number
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        raise


def send_email_code(user, code):
    """
    Send reset code via email
    """
    subject = "Password Reset Code"
    message = (
        f"Your password reset code is: {code}\n\nThis code will expire in 10 minutes."
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise
