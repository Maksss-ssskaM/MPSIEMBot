from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.settings import Settings
from filters import IsAdmin
from handlers.admin_router.user_list import user_list
from handlers.admin_router.settings import settings_menu
from keyboards import create_main_menu, create_settings_menu
from lexicons import SETTINGS_LEXICON
from services import user_service
from services.settings_service import SettingsHandler
from services.siem_service import SiemHandler

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

router.include_routers(settings_menu.router, user_list.router)


@router.message(Command('menu'))
async def process_menu_command(message: Message):
    return await message.answer(
        text='Выберите действие в меню:',
        reply_markup=create_main_menu('get_last_incidents', 'get_incident_by_id', 'settings', 'users', width=2)
    )


@router.message(F.text == 'Настройки ⚙️')
@router.callback_query(F.data == 'settings')
async def process_settings_menu_message(update: Message | CallbackQuery):
    pause_time, time_zone = SettingsHandler.pause_time, SettingsHandler.time_zone
    is_working = SiemHandler.is_working

    text = SETTINGS_LEXICON['settings_menu'].format(
        pause_time=pause_time,
        time_zone=time_zone,
        is_launch='Запущен ✅' if is_working else 'Остановлен ❌'
    )

    if isinstance(update, CallbackQuery):
        return await update.message.edit_text(
            text=text,
            reply_markup=create_settings_menu()
        )

    return await update.answer(
        text=text,
        reply_markup=create_settings_menu()
    )


@router.message(F.text == 'Пользователи 👥')
async def process_get_all_users_command(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    users_info, reply_markup = await user_service.display_users_in_list(
        session=session,
        state=state,
        current_page=0,
        users_per_page=5
    )

    return await message.answer(text=users_info, reply_markup=reply_markup)
