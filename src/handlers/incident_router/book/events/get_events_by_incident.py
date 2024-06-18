from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import IncidentsBookActions, create_incident_info_kb
from database.query_service import get_incident_by_id
from services import incident_service

router = Router()


@router.callback_query(IncidentsBookActions.filter(F.action == 'incident_info'))
async def get_events_by_incident(callback: CallbackQuery, session: AsyncSession, callback_data: IncidentsBookActions):
    incident = await get_incident_by_id(session=session, incident_id=callback_data.incident_id)
    incident_info = await incident_service.get_incident_and_events_info(incident=incident)
    return await callback.message.edit_text(
        text=incident_info,
        reply_markup=create_incident_info_kb(incident_id=incident.incident_id)
    )


@router.callback_query(F.data == 'back_to_incident_book')
async def back_to_book(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    book_data = await state.get_data()
    incidents_info, reply_markup = await incident_service.display_incidents_in_book(
        session=session,
        state=state,
        current_page=book_data['incident_book_current_page'],
        incidents_per_page=book_data['incidents_per_page']
    )

    return await callback.message.edit_text(text=incidents_info, reply_markup=reply_markup)
