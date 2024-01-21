from django.core.exceptions import ObjectDoesNotExist

from api.tg_shop_bot.models import TgAdmin


async def get_user_by_id(user_id):
    try:
        return TgAdmin.objects.get(telegram_id=user_id)
    except ObjectDoesNotExist:
        return None
