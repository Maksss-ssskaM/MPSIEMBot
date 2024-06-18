import asyncio
from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import create_settings_menu
from lexicons import SETTINGS_LEXICON
from services.siem_service import SiemHandler
from services.settings_service import SettingsHandler

router = Router()


@router.callback_query(F.data == 'launch')
async def launch(callback: CallbackQuery, bot: Bot, session: AsyncSession):
    pause_time, time_zone = SettingsHandler.pause_time, SettingsHandler.time_zone
    SiemHandler.toggle_working_status()
    with suppress(TelegramBadRequest):
        msg = await callback.message.edit_text(
            text=SETTINGS_LEXICON['settings_menu'].format(
                pause_time=pause_time,
                time_zone=time_zone,
                is_launch='Запущен ✅' if SiemHandler.is_working else 'Остановлен ❌'
            ),
            reply_markup=create_settings_menu()
        )

    if SiemHandler.is_working:
        siem_task = asyncio.create_task(SiemHandler.get_siem_incidents(bot=bot, session=session))
        SiemHandler.siem_task = siem_task
        await callback.answer("Система запущена")
    else:
        await callback.answer("Система остановлена")
        if SiemHandler.siem_task and not SiemHandler.siem_task.done():
            await SiemHandler.siem_task
    return msg
