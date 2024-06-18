from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from filters import IsRegistered, IsAuthorized
from keyboards import create_main_menu, create_user_account_kb
from database.query_service import get_user
from services import user_service
from .account import account_operations

router = Router()
router.message.filter(IsRegistered(), IsAuthorized())
router.callback_query.filter(IsRegistered(), IsAuthorized())

router.include_routers(account_operations.router)


@router.message(Command('menu'))
async def process_menu_command(message: Message):
    return await message.answer(
        text='Выберите действие в меню:',
        reply_markup=create_main_menu('get_last_incidents', 'get_incident_by_id', 'account', width=2)
    )


@router.message(F.text == 'Личный кабинет 💼')
async def process_account_command(message: Message, session: AsyncSession):
    user = await get_user(session=session, user_id=message.from_user.id)
    account_info = user_service.get_user_info(user=user, online_session=user.online_session)

    return await message.answer(
        text=account_info, reply_markup=create_user_account_kb('change_password', 'close_session')
    )
