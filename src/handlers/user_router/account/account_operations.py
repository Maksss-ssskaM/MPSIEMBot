from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import create_confirm_new_password_kb
from lexicons import ACCOUNT_LEXICON
from services import auth_service
from services.auth_service import is_valid_password
from states import FSMAccount

router = Router()


@router.callback_query(F.data == 'close_session')
async def process_close_session(callback: CallbackQuery, session: AsyncSession, scheduler: AsyncIOScheduler):
    await auth_service.logout_user(session=session, user_id=callback.from_user.id, scheduler=scheduler)
    return await callback.message.edit_text(
        text=ACCOUNT_LEXICON['answers']['session_closed']
    )


@router.callback_query(F.data == 'change_password')
async def process_change_password(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMAccount.get_new_password)
    return await callback.message.edit_text(text=ACCOUNT_LEXICON['answers']['get_new_password'])


@router.message(F.text, FSMAccount.get_new_password)
async def process_get_new_password(message: Message, state: FSMContext):
    await message.delete()
    new_password = message.text
    if not is_valid_password(new_password):
        return await message.answer(text=ACCOUNT_LEXICON['answers']['incorrect_new_password'])

    await state.set_state(FSMAccount.confirm_password)
    await state.update_data(new_password=new_password)
    return await message.answer(
        text=ACCOUNT_LEXICON['answers']['confirm_password'].format(new_password=new_password),
        reply_markup=create_confirm_new_password_kb()
    )


@router.callback_query(F.data == 'confirm_new_password', FSMAccount.confirm_password)
async def process_confirm_password(callback: CallbackQuery, state: FSMContext, session: AsyncSession, scheduler: AsyncIOScheduler):
    user_id = callback.from_user.id
    data = await state.get_data()
    new_password = await auth_service.create_password(user_id=user_id, session=session,
                                                      new_password=data['new_password'])
    await auth_service.logout_user(session=session, user_id=user_id, scheduler=scheduler)
    await state.clear()
    return await callback.message.edit_text(
        text=ACCOUNT_LEXICON['answers']['change_password'].format(new_password=new_password)
    )


@router.message(FSMAccount.confirm_password)
async def process_confirmation_password_err(message: Message):
    return await message.answer(text=ACCOUNT_LEXICON['answers']['password_confirmation_err'])
