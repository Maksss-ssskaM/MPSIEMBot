from datetime import timedelta
from math import ceil
from typing import Sequence
from uuid import UUID

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from config_data import load_config
from database.models.event import Event
from database.models.incident import Incident
from keyboards import create_incident_book_kb
from database.query_service import get_incidents, get_incident_by_id
from services.settings_service import SettingsHandler

config = load_config()


def incident_details(incident: Incident) -> str:
    date = (incident.created_at + timedelta(hours=SettingsHandler.time_zone)).strftime('%d.%m.%Y (%H:%M:%S)')
    link = f'{config.settings.base_url}/#/incident/incidents/view/{incident.incident_id}'

    return f'————————————————————\n' \
           f'<b>{incident.key}</b>\n' \
           f'————————————————————\n' \
           f'<b><a href="{link}">➡️ Ссылка</a></b>\n\n' \
           f'<b>Статус:</b> {incident.status.value}\n' \
           f'<b>Тип:</b> {incident.type}\n' \
           f'<b>Имя:</b> {incident.name}\n' \
           f'<b>Уровень:</b> {incident.severity.value}\n\n' \
           f'<b>Дата:</b> {date}\n\n\n'


def event_details(event: Event) -> str:
    date = (event.created_at + timedelta(hours=SettingsHandler.time_zone)).strftime('%d.%m.%Y (%H:%M:%S)')

    return f'\n\n' \
           f'<b>Дата:</b> {date}\n' \
           f'<b>Событие:</b>\n{event.description}'


async def get_incidents_for_book(session: AsyncSession, skip: int, limit: int,
                                 **filter_and_sort_options) -> (str, Sequence[Incident]):

    incidents, incidents_count = await get_incidents(session=session, skip=skip, limit=limit,
                                    **filter_and_sort_options)
    if incidents:
        incidents_info = ''
        for incident in incidents:
            incidents_info += incident_details(incident=incident)
    else:
        incidents_info = '⚠️ Список инцидентов пуст!'

    return incidents_info, incidents, incidents_count


async def display_incidents_in_book(session: AsyncSession, state: FSMContext, current_page: int,
                                    incidents_per_page: int) -> tuple[str, InlineKeyboardMarkup]:
    if current_page < 0 or incidents_per_page <= 0:
        raise ValueError("Некорректные значения current_page и incidents_per_page")

    skip = current_page * incidents_per_page

    data = await state.get_data()
    incidents_info, incidents, total_incidents_count = await get_incidents_for_book(
        session=session,
        skip=skip,
        limit=incidents_per_page,
        date_sort=data.get('date_sort'),
        severity=data.get('severity'),
        status=data.get('status')
    )

    total_pages = ceil(total_incidents_count / incidents_per_page)

    await state.update_data(incident_book_current_page=current_page, incidents_per_page=incidents_per_page,
                            total_pages=total_pages)

    if current_page == 0 and total_pages > 1:
        reply_markup = create_incident_book_kb('incidents_right', incidents=incidents,
                                               incidents_per_page=incidents_per_page)
    elif 0 < current_page < total_pages - 1:
        reply_markup = create_incident_book_kb('incidents_left', 'incidents_right', incidents=incidents,
                                               incidents_per_page=incidents_per_page)
    elif current_page > 0 and current_page == total_pages - 1:
        reply_markup = create_incident_book_kb('incidents_left', incidents=incidents,
                                               incidents_per_page=incidents_per_page)
    else:
        reply_markup = None

    return incidents_info, reply_markup


async def get_incident_and_events_info(incident: Incident) -> str:
    incident_info = incident_details(incident=incident)
    events = incident.events
    if events:
        incident_info += '<b>----- События -----</b>'
        for event in events:
            incident_info += event_details(event=event)
    else:
        incident_info += '⚠️ События не найдены'

    return incident_info


async def update_incident_info(session: AsyncSession, incident_id: UUID, update_fields: dict):
    incident = await get_incident_by_id(session=session, incident_id=incident_id)

    for field, value in update_fields.items():
        setattr(incident, field, value)

    await session.flush()

    return incident