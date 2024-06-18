from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession

from lexicons import AUTH_LEXICON
from database.query_service import get_user
from services import auth_service
from services.auth_service import password_hasher
from states import FSMLoginUser

router = Router()


@router.message(Command('login'))
async def process_login_user_command(message: Message, state: FSMContext, session: AsyncSession):
    user = await get_user(user_id=message.from_user.id, session=session)

    if not user:
        return await message.answer(text=AUTH_LEXICON['login']['not_registered'])

    user_session = user.online_session
    if not user_session.online:
        await state.set_state(FSMLoginUser.get_password)
        await state.update_data(password=user.password)
        return await message.answer(text=AUTH_LEXICON['login']['enter_password'])

    return await message.answer(text=AUTH_LEXICON['login']['already_logged_in'])


@router.message(F.text, FSMLoginUser.get_password)
async def process_get_password_for_login_user(message: Message, state: FSMContext, session: AsyncSession,
                                              scheduler: AsyncIOScheduler):
    data = await state.get_data()

    try:
        password_hasher.verify(password=message.text, hash=data['password'])
        await auth_service.login_user(user_id=message.from_user.id, session=session, scheduler=scheduler)
        await message.delete()
        await state.clear()
        return await message.answer(text=AUTH_LEXICON['login']['success_login'])
    except VerifyMismatchError:
        return await message.answer(text=AUTH_LEXICON['login']['incorrect_password'])


@router.message(FSMLoginUser.get_password)
async def process_incorrect_password(message: Message):
    return await message.answer(text=AUTH_LEXICON['login']['invalid_password'])
