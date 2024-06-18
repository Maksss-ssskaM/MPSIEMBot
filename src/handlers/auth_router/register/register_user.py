import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession

from config_data import load_config
from keyboards import create_confirm_user_kb
from keyboards.admin_keyboards import UserRegistrationActions
from lexicons import AUTH_LEXICON
from database.query_service import get_user
from services import auth_service
from services.auth_service import password_hasher
from services.settings_service import SettingsHandler
from states import FSMRegUser

router = Router()
config = load_config()


@router.message(Command('reg'))
async def process_register_user_command(message: Message, state: FSMContext, session: AsyncSession):
    user = await get_user(user_id=message.from_user.id, session=session)
    if user:
        return await message.answer(text=AUTH_LEXICON['registration']['already_registered'])

    await state.set_state(FSMRegUser.get_password)
    return await message.answer(
        text=AUTH_LEXICON['registration']['request_password'].format(admin_id=config.settings.admin_id))


@router.message(F.text, FSMRegUser.get_password)
async def process_get_password_for_register_user(message: Message, state: FSMContext, bot: Bot):
    try:
        if SettingsHandler.reg_pass is None:
            return await message.answer(text="Начальная настройка бота не была произведена.")

        password_hasher.verify(password=message.text, hash=SettingsHandler.reg_pass)
        user = message.from_user
        await message.answer(text=AUTH_LEXICON['registration']['password_accepted'])
        await state.clear()

        return await bot.send_message(
            chat_id=config.settings.admin_id,
            text=AUTH_LEXICON['registration']['user_access_request'].format(username=user.username),
            reply_markup=create_confirm_user_kb(user=user)
        )
    except VerifyMismatchError:
        return await message.answer(text=AUTH_LEXICON['registration']['password_not_accepted'])


@router.message(FSMRegUser.get_password)
async def process_incorrect_password(message: Message):
    return await message.answer(text=AUTH_LEXICON['registration']['invalid_password'])


@router.callback_query(UserRegistrationActions.filter(F.action == 'confirm_reg'))
async def process_confirm_register(callback: CallbackQuery, session: AsyncSession, callback_data: UserRegistrationActions, bot: Bot):
    user_id, username = callback_data.user_id, callback_data.username

    await auth_service.register_user(session=session, user_id=user_id, username=username)
    reg_pass = await auth_service.create_password(user_id=user_id, session=session)

    await callback.message.edit_text(
        text=AUTH_LEXICON['registration']['success'].format(username=username)
    )
    message = await bot.send_message(
        chat_id=user_id,
        text=AUTH_LEXICON['registration']['approve_message'].format(reg_pass=reg_pass)
    )

    await asyncio.sleep(300)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=AUTH_LEXICON['registration']['approve_message_hidden']
    )


@router.callback_query(UserRegistrationActions.filter(F.action == 'reject_reg'))
async def process_reject_register(callback: CallbackQuery, callback_data: UserRegistrationActions, bot: Bot):
    await callback.message.edit_text(
        text=AUTH_LEXICON['registration']['reject'].format(username=callback_data.username)
    )
    return await bot.send_message(chat_id=callback_data.user_id, text=AUTH_LEXICON['registration']['reject_reply'])
