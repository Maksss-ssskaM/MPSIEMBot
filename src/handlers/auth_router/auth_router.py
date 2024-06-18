from aiogram import Router

from .login import login_user
from .register import register_user

router = Router()
router.include_routers(register_user.router, login_user.router)