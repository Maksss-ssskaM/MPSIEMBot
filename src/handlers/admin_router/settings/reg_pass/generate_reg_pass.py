from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from lexicons import SETTINGS_LEXICON
from services.settings_service import SettingsHandler

router = Router()


@router.callback_query(F.data == 'new_reg_pass')
async def process_generate_new_reg_password(callback: CallbackQuery, session: AsyncSession):
    new_password = await SettingsHandler.new_reg_pass(session=session)
    message = await callback.message.edit_text(
        text=SETTINGS_LEXICON['reg_pass']['new_pass'].format(new_pass=new_password),
    )
    return message, new_password
