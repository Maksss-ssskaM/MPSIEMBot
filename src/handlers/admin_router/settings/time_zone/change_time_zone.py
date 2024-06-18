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


@router.callback_query(F.data == 'new_time_zone')
async def process_new_time_zone_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMNewParameter.new_time_zone)
    msg = await callback.message.edit_text(
        text=SETTINGS_LEXICON['time_zone']['info'],
        reply_markup=back_kb(button='settings')
    )
    await state.update_data(msg_id=msg.message_id)
    return msg


@router.message(lambda m: m.text and m.text.isdigit() and -12 <= int(m.text) <= 13, FSMNewParameter.new_time_zone)
async def process_time_zone_input(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
    data = await state.get_data()
    with suppress(TelegramBadRequest):
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['msg_id'],
                                            reply_markup=delete_kb())
    new_time_zone = int(message.text)
    await SettingsHandler.new_time_zone(session=session, new_time_zone=new_time_zone)
    await state.clear()
    return await message.answer(text=SETTINGS_LEXICON['time_zone']['successfully'].format(new_time_zone=new_time_zone))


@router.message(FSMNewParameter.new_time_zone)
async def process_incorrect_time_zone_input(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    with suppress(TelegramBadRequest):
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['msg_id'],
                                            reply_markup=delete_kb())
    return await message.answer(text=SETTINGS_LEXICON['time_zone']['incorrect'])
