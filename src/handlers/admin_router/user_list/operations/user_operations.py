import asyncio

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import UsersListActions, confirm_reject_user_deletion_kb
from lexicons import USER_LIST_LEXICON
from services import user_service, auth_service

router = Router()


@router.callback_query(UsersListActions.filter(F.action == 'close_session'))
async def process_close_user_session(callback: CallbackQuery, callback_data: UsersListActions,
                                     session: AsyncSession, scheduler: AsyncIOScheduler, bot: Bot):
    await callback.message.delete()
    user_id = callback_data.user_id
    username = callback_data.username
    await auth_service.logout_user(session=session, user_id=user_id, scheduler=scheduler)

    await callback.message.answer(
        text=USER_LIST_LEXICON['answers']['admin']['session_closed'].format(username=username)
    )
    return await bot.send_message(
        chat_id=user_id,
        text=USER_LIST_LEXICON['answers']['user']['session_closed']
    )


@router.callback_query(UsersListActions.filter(F.action == 'generate_new_password'))
async def process_generate_new_user_password(callback: CallbackQuery, callback_data: UsersListActions,
                                             session: AsyncSession, scheduler: AsyncIOScheduler, bot: Bot):
    await callback.message.delete()
    user_id = callback_data.user_id
    username = callback_data.username
    new_password = await auth_service.create_password(user_id=user_id, session=session)
    await auth_service.logout_user(session=session, user_id=user_id, scheduler=scheduler)

    await callback.message.answer(
        text=USER_LIST_LEXICON['answers']['admin']['new_password_created'].format(username=username)
    )
    message = await bot.send_message(
        chat_id=user_id,
        text=USER_LIST_LEXICON['answers']['user']['new_password_created'].format(new_password=new_password)
    )
    await asyncio.sleep(300)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=USER_LIST_LEXICON['answers']['user']['new_password_created_hidden'].format(new_password=new_password)
    )


@router.callback_query(UsersListActions.filter(F.action == 'delete_user'))
async def process_delete_user(callback: CallbackQuery, callback_data: UsersListActions):
    await callback.message.delete()
    user_id = callback_data.user_id
    username = callback_data.username
    return await callback.message.answer(
        text=USER_LIST_LEXICON['answers']['admin']['confirm_user_deletion'].format(username=username),
        reply_markup=confirm_reject_user_deletion_kb(user_id=user_id, username=username)
    )


@router.callback_query(UsersListActions.filter(F.action == 'confirm_user_deletion'))
async def process_confirm_user_deletion(callback: CallbackQuery, callback_data: UsersListActions, session: AsyncSession,
                                        bot: Bot):
    user_id = callback_data.user_id
    username = callback_data.username
    await user_service.delete_user(user_id=user_id, session=session)
    await callback.message.edit_text(
        text=USER_LIST_LEXICON['answers']['admin']['user_deleted'].format(username=username),
    )
    return await bot.send_message(
        chat_id=user_id,
        text=USER_LIST_LEXICON['answers']['user']['user_deleted']
    )
