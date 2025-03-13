# backend\message\management\commands\start_telegram_bot.py:

import logging
from django.core.management.base import BaseCommand
from message.telegram_bot import run_bot

logger = logging.getLogger(__name__)

# ~~~~~~~~~~~~~~~~~~~~ MESSAGE ~~~~~~~~~~~~~~~~~~~~


class Command(BaseCommand):
    help = "Starts the Telegram bot for password reset functionality"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Telegram bot..."))
        logger.info("Starting Telegram bot via management command")

        try:
            run_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Telegram bot stopped"))
        except Exception as e:
            logger.error(f"Error in Telegram bot: {str(e)}")
            self.stdout.write(self.style.ERROR(f"Error in Telegram bot: {str(e)}"))
