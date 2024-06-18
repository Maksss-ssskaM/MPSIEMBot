from aiogram import Router

from .launch import launch
from .pause_time import change_pause_time
from .reg_pass import generate_reg_pass
from .time_zone import change_time_zone

router = Router()
router.include_routers(change_pause_time.router, change_time_zone.router, generate_reg_pass.router, launch.router)
