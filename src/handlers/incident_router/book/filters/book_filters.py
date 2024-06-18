from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import create_filter_kb
from lexicons import FILTER_LEXICON, INCIDENTS_LEXICON
from services import incident_service

router = Router()


@router.callback_query(F.data == 'book_filter')
async def process_book_filter(callback: CallbackQuery, state: FSMContext):
    return await callback.message.edit_text(
        text=INCIDENTS_LEXICON['filter_menu'],
        reply_markup=await create_filter_kb(state=state)
    )


@router.callback_query(F.data.in_(FILTER_LEXICON['date_sorting']))
async def process_date_sorting(callback: CallbackQuery, state: FSMContext):
    sorting_mapping = {'newest_first': 'oldest_first', 'oldest_first': 'newest_first'}
    new_sorting = sorting_mapping[callback.data]
    await state.update_data(date_sort=new_sorting)
    return await callback.message.edit_reply_markup(reply_markup=await create_filter_kb(state=state))


@router.callback_query(F.data.in_(FILTER_LEXICON['severity_filter']))
async def process_severity_filter(callback: CallbackQuery, state: FSMContext):
    severity_mapping = {
        'default_severity': 'high_severity', 'high_severity': 'medium_severity',
        'medium_severity': 'low_severity', 'low_severity': 'default_severity'
    }
    new_filter = severity_mapping[callback.data]
    await state.update_data(severity=new_filter)
    return await callback.message.edit_reply_markup(reply_markup=await create_filter_kb(state=state))


@router.callback_query(F.data.in_(FILTER_LEXICON['status_filter']))
async def process_status_filter(callback: CallbackQuery, state: FSMContext):
    status_mapping = {
        'default_status': 'new_status', 'new_status': 'approved_status', 'approved_status': 'in_progress_status',
        'in_progress_status': 'resolved_status', 'resolved_status': 'closed_status', 'closed_status': 'default_status'
    }
    new_filter = status_mapping[callback.data]
    await state.update_data(status=new_filter)
    return await callback.message.edit_reply_markup(reply_markup=await create_filter_kb(state=state))


@router.callback_query(F.data == 'apply_filter')
async def process_apply_filter(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    incidents_info, reply_markup = await incident_service.display_incidents_in_book(
        session=session,
        state=state,
        current_page=0,
        incidents_per_page=3
    )

    await callback.message.edit_text(text=incidents_info, reply_markup=reply_markup)