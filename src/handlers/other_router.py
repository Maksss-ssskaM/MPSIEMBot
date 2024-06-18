from aiogram import Router
from aiogram.types import Message, CallbackQuery

from filters import IsAuthorized, IsRegistered
from lexicons import OTHER_LEXICON, ACCOUNT_LEXICON

router = Router()


@router.message(~IsRegistered())
@router.callback_query(~IsRegistered())
async def not_registered(update: Message | CallbackQuery):
    if isinstance(update, CallbackQuery):
        update = update.message
    return await update.answer(text=ACCOUNT_LEXICON['register_notification'])


@router.message(~IsAuthorized())
@router.callback_query(~IsAuthorized())
async def not_authorized(update: Message | CallbackQuery):
    if isinstance(update, CallbackQuery):
        update = update.message
    return await update.answer(text=ACCOUNT_LEXICON['login_notification'])


@router.message()
async def unrecognized_message(message: Message):
    return await message.answer(text=OTHER_LEXICON['unrecognized_message'])
