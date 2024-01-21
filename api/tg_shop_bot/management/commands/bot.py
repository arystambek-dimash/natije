import os

import django
from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

from .routers import router
from aiogram.fsm.storage.memory import MemoryStorage

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rest.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


class Command(BaseCommand):
    help = "Telegram bot"

    def handle(self, *args, **options):
        bot = Bot(token=settings.TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(router=router)
        dp.run_polling(bot)