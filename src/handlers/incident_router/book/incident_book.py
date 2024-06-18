from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from services import incident_service
from .events import get_events_by_incident
from .filters import book_filters

router = Router()

router.include_routers(book_filters.router, get_events_by_incident.router)


@router.message(F.text == 'Получить последние инциденты 📜')
async def process_get_last_incidents_command(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    incidents_info, reply_markup = await incident_service.display_incidents_in_book(
        session=session,
        state=state,
        current_page=0,
        incidents_per_page=3
    )

    return await message.answer(text=incidents_info, reply_markup=reply_markup)


@router.callback_query(F.data == 'incidents_right')
async def process_right_incident_book(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    current_page = data.get('incident_book_current_page') + 1
    incidents_per_page = data.get('incidents_per_page')

    incidents_info, reply_markup = await incident_service.display_incidents_in_book(
        session=session,
        state=state,
        current_page=current_page,
        incidents_per_page=incidents_per_page
    )

    await callback.message.edit_text(text=incidents_info, reply_markup=reply_markup)


@router.callback_query(F.data == 'incidents_left')
async def process_left_incident_book(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    current_page = data.get('incident_book_current_page')
    incidents_per_page = data.get('incidents_per_page')

    if current_page > 0:
        current_page -= 1

    incidents_info, reply_markup = await incident_service.display_incidents_in_book(
        session=session,
        state=state,
        current_page=current_page,
        incidents_per_page=incidents_per_page
    )

    await callback.message.edit_text(text=incidents_info, reply_markup=reply_markup)


@router.callback_query(F.data == 'change_incidents_quantity_per_page')
async def process_change_incidents_quantity_per_page(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()

    incidents_per_page = data.get('incidents_per_page', 3)
    incidents_per_page = 3 if incidents_per_page == 5 else incidents_per_page + 1

    current_page = 0

    incidents_info, reply_markup = await incident_service.display_incidents_in_book(
        session=session,
        state=state,
        current_page=current_page,
        incidents_per_page=incidents_per_page
    )

    await state.update_data(incidents_per_page=incidents_per_page, incident_book_current_page=current_page)
    return await callback.message.edit_text(text=incidents_info, reply_markup=reply_markup)
