from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.incident import IncidentStatus, IncidentSeverity
from external_services.max_patrol_10 import get_incident_by_incident_id, update_incident_by_incident_id
from keyboards import UpdateIncidentActions, create_update_incident_kb, create_selection_keyboard, create_incident_info_kb
from services import incident_service
from states.incident_states import FSMUpdateIncident

router = Router()


@router.callback_query(UpdateIncidentActions.filter(F.action == 'menu'))
async def update_incident_menu(callback: CallbackQuery, callback_data: UpdateIncidentActions):
    await callback.message.edit_reply_markup(
        reply_markup=create_update_incident_kb(incident_id=callback_data.incident_id)
    )


@router.callback_query(UpdateIncidentActions.filter(F.action.in_(['name', 'status', 'severity'])))
async def initiate_update_incident_property(callback: CallbackQuery, state: FSMContext,
                                            callback_data: UpdateIncidentActions):
    incident_id = callback_data.incident_id
    prompt_text = ''

    await state.update_data(incident_id=str(incident_id), message_id=callback.message.message_id)

    if callback_data.action == 'name':
        await state.set_state(FSMUpdateIncident.waiting_for_name)
        prompt_text = 'Введите новое имя:'
    elif callback_data.action == 'status':
        await state.set_state(FSMUpdateIncident.waiting_for_status)
        prompt_text = 'Выберите новый статус:'
    elif callback_data.action == 'severity':
        await state.set_state(FSMUpdateIncident.waiting_for_severity)
        prompt_text = 'Выберите новую серьезность:'
    await callback.message.edit_text(text=prompt_text,
                                     reply_markup=create_selection_keyboard(action=callback_data.action,
                                                                            incident_id=callback_data.incident_id))


@router.message(F.text, FSMUpdateIncident.waiting_for_name)
async def update_incident_name(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = await state.get_data()

    incident_response = await get_incident_by_incident_id(incident_id=data['incident_id'])
    if incident_response.status_code != 200:
        return await message.answer(text='Не удалось получить информацию об инциденте.')

    incident_data = incident_response.json()
    incident_data['name'] = message.text

    update_incident_response = await update_incident_by_incident_id(incident_data=incident_data)
    if update_incident_response.status_code != 204:
        return await message.answer(text='Не удалось изменить имя инцидента.')

    incident = await incident_service.update_incident_info(session, data['incident_id'], {'name': message.text})
    incident_info = await incident_service.get_incident_and_events_info(incident=incident)

    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=data['message_id'],
        text=incident_info,
        reply_markup=create_incident_info_kb(incident_id=data['incident_id'])
    )

    await message.answer(text='Имя инцидента успешно изменено.')


@router.callback_query(
    UpdateIncidentActions.filter(F.action.in_(['New', 'Approved', 'InProgress', 'Resolved', 'Closed'])))
async def update_incident_status(callback: CallbackQuery, state: FSMContext, callback_data: UpdateIncidentActions,
                                 session: AsyncSession, bot: Bot):
    data = await state.get_data()

    incident_response = await get_incident_by_incident_id(incident_id=data['incident_id'])
    if incident_response.status_code != 200:
        return await callback.message.answer(text='Не удалось получить информацию об инциденте.')

    incident_data = incident_response.json()
    incident_data['status'] = callback_data.action

    update_incident_response = await update_incident_by_incident_id(incident_data=incident_data)
    if update_incident_response.status_code != 204:
        return await callback.message.answer(text='Не удалось изменить статус инцидента.')

    incident = await incident_service.update_incident_info(session, data['incident_id'],
                                          {'status': getattr(IncidentStatus, callback_data.action)})
    incident_info = await incident_service.get_incident_and_events_info(incident=incident)

    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=data['message_id'],
        text=incident_info,
        reply_markup=create_incident_info_kb(incident_id=data['incident_id'])
    )
    await callback.message.answer(text='Статус инцидента успешно изменен.')


@router.callback_query(UpdateIncidentActions.filter(F.action.in_(['High', 'Medium', 'Low'])))
async def update_incident_severity(callback: CallbackQuery, state: FSMContext, callback_data: UpdateIncidentActions,
                                   session: AsyncSession, bot: Bot):
    data = await state.get_data()

    incident_response = await get_incident_by_incident_id(incident_id=data['incident_id'])
    if incident_response.status_code != 200:
        return await callback.message.answer(text='Не удалось получить информацию об инциденте.')

    incident_data = incident_response.json()
    incident_data['severity'] = callback_data.action

    update_incident_response = await update_incident_by_incident_id(incident_data=incident_data)
    if update_incident_response.status_code != 204:
        return await callback.message.answer(text='Не удалось изменить уровень угрозы инцидента.')

    incident = await incident_service.update_incident_info(session, data['incident_id'],
                                          {'severity': getattr(IncidentSeverity, callback_data.action)})
    incident_info = await incident_service.get_incident_and_events_info(incident=incident)

    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=data['message_id'],
        text=incident_info,
        reply_markup=create_incident_info_kb(incident_id=data['incident_id'])
    )

    await callback.message.answer(text='Уровень угрозы инцидента успешно изменен.')
