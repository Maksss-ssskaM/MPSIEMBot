from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import back_kb, delete_kb
from lexicons import SETTINGS_LEXICON
from services.settings_service import SettingsHandler
from states import FSMNewParameter

router = Router()


@router.callback_query(F.data == 'new_pause_time')
async def process_new_pause_time_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMNewParameter.new_pause_time)
    msg = await callback.message.edit_text(
        text=SETTINGS_LEXICON['pause_time']['info'],
        reply_markup=back_kb(button='settings')
    )
    await state.update_data(msg_id=msg.message_id)
    return msg


@router.message(lambda m: m.text and m.text.isdigit() and int(m.text) > 0, FSMNewParameter.new_pause_time)
async def process_pause_time_input(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
    data = await state.get_data()
    with suppress(TelegramBadRequest):
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['msg_id'],
                                            reply_markup=delete_kb())
    new_pause_time = int(message.text)
    await SettingsHandler.new_pause_time(session=session, new_pause_time=new_pause_time)
    await state.clear()
    return await message.answer(text=SETTINGS_LEXICON['pause_time']['successfully'].format(new_pause_time=new_pause_time))


@router.message(FSMNewParameter.new_pause_time)
async def process_incorrect_pause_time_input(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    with suppress(TelegramBadRequest):
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['msg_id'],
                                            reply_markup=delete_kb())
    return await message.answer(text=SETTINGS_LEXICON['pause_time']['incorrect'])
