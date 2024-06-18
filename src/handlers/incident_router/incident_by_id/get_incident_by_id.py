from uuid import UUID

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import create_incident_info_kb
from lexicons import INCIDENTS_LEXICON
from database.query_service import get_incident_by_id, get_incident_by_key
from services import incident_service
from states import FSMIncidents

router = Router()


@router.message(F.text == 'Получить инцидент по id / ключу 🔍')
async def process_get_incident_by_id_command(message: Message, state: FSMContext):
    await state.set_state(FSMIncidents.get_incident_id)
    return await message.answer(text=INCIDENTS_LEXICON['enter_id_key'])


@router.message(F.text, FSMIncidents.get_incident_id)
async def process_incident_id_input(message: Message, state: FSMContext, session: AsyncSession):
    try:
        incident = await get_incident_by_id(session=session, incident_id=UUID(message.text))
    except ValueError:
        incident = await get_incident_by_key(session=session, key=message.text)

    if incident:
        incident_info = await incident_service.get_incident_and_events_info(incident=incident)
    else:
        incident_info = INCIDENTS_LEXICON['incorrect_id_key']

    await state.clear()
    return await message.answer(text=incident_info, reply_markup=create_incident_info_kb(incident_id=incident.incident_id))