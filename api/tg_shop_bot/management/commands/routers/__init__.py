from aiogram import Router
from ..utils import import_routers

router = Router()

import_routers(__name__)