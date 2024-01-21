from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter

from . import router
from api.tg_shop_bot.models import TgAdmin
from .utils import get_user_by_id


class LoginForm(StatesGroup):
    GET_PIN_CODE = State()


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    try:
        user = await get_user_by_id(msg.from_user.id)
    except TgAdmin.DoesNotExist:
        pass
    if not user:
        await msg.answer("Pin code: ")
        await state.set_state(LoginForm.GET_PIN_CODE)
    else:
        kb = ReplyKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Курстар", callback_data='Ru'),
             InlineKeyboardButton(text="Тест", callback_data='Kz')]
        ])
        await msg.answer("Таңдаңыз", reply_markup=kb)


@router.message(StateFilter(LoginForm.GET_PIN_CODE))
async def progress_code(msg: Message, state: FSMContext):
    pin_code = msg.text.strip()
    if pin_code == "12345678":
        TgAdmin.objects.get_or_create(telegram_id=msg.from_user.id)
        await state.set_state(LoginForm.GET_PIN_CODE)
    else:
        await msg.answer("Қате pin. Қайтадан бастау /start")
