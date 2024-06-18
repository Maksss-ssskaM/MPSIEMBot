import asyncio
from datetime import datetime, timedelta
from typing import Sequence, Dict

import httpx
from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from config_data import load_config
from database import Event, Incident, get_session_maker
from database.models.incident import IncidentSeverity, IncidentStatus
from external_services import max_patrol_10, web_app
from database.query_service import get_settings, get_users
from services.settings_service import SettingsHandler

config = load_config()


def parse_iso_datetime(date_str):
    if date_str.endswith('Z'):
        date_str = date_str[:-1]

    if '.' in date_str:
        base, fraction = date_str.split('.')
        fraction = fraction[:6]
        date_str = f'{base}.{fraction}'

    try:
        return datetime.fromisoformat(date_str)
    except ValueError as e:
        print(f"Ошибка при разборе даты: {e}")
        return None


class SiemHandler:
    siem_task = None
    is_working: bool = False
    __session_maker = get_session_maker()

    @classmethod
    def toggle_working_status(cls) -> None:
        cls.is_working = not cls.is_working

    @classmethod
    async def get_siem_incidents(cls, bot: Bot, session: AsyncSession) -> None:
        try:
            while cls.is_working:
                incidents = await max_patrol_10.get_siem_incidents(last_incident_time=SettingsHandler.last_incident_time)
                if incidents:
                    await cls.save_incidents_and_events(incidents=incidents, session=session)
                    await cls.send_new_incidents_info(incidents=incidents, session=session, bot=bot)
                    settings = await get_settings(session=session)
                    settings.last_incident_time = SettingsHandler.last_incident_time
                await session.commit()
                await asyncio.sleep(SettingsHandler.pause_time)
        except httpx.HTTPError as http_err:
            await bot.send_message(
                chat_id=config.settings.admin_id,
                text=f'🚫 <b>Ошибка подключения</b>\n\n'
                     f'Причина: {http_err}'
            )

    @staticmethod
    async def save_incidents_and_events(incidents: Sequence[Dict], session: AsyncSession) -> None:

        for incident in incidents:
            created_at = parse_iso_datetime(incident['created'])
            if created_at > SettingsHandler.last_incident_time:
                SettingsHandler.last_incident_time = created_at + timedelta(milliseconds=1)
            incident_id, key, name, status, _type, severity = \
                incident['id'], incident['key'], incident['name'], incident['status'], incident['type'], incident[
                    'severity']

            await session.execute(
                insert(Incident).
                values(
                    incident_id=incident_id,
                    key=key,
                    name=name,
                    status=status,
                    type=_type,
                    created_at=created_at,
                    severity=severity
                ).
                on_conflict_do_update(
                    index_elements=['incident_id'],
                    set_={
                        'incident_id': incident_id,
                        'key': key,
                        'name': name,
                        'status': status,
                        'type': _type,
                        'created_at': created_at,
                        'severity': severity
                    }
                )
            )

            events = await max_patrol_10.get_siem_events_by_incident_id(incident_id=incident['id'])
            if events:
                for event in events:
                    created_at = parse_iso_datetime(event['date'])
                    incident_id, event_id, description = incident['id'], event['id'], event['description']

                    await session.execute(
                        insert(Event).
                        values(
                            incident_id=incident_id,
                            event_id=event_id,
                            created_at=created_at,
                            description=description
                        ).
                        on_conflict_do_update(
                            index_elements=['event_id'],
                            set_={
                                'incident_id': incident_id,
                                'event_id': event_id,
                                'created_at': created_at,
                                'description': description,
                            }
                        )
                    )

    @staticmethod
    async def send_new_incidents_info(incidents: Sequence[Dict], session: AsyncSession, bot: Bot) -> Message:
        intro_message = '🔎⚠️ <b>Найдены новые инциденты и/или изменения!</b>\n\n'
        new_incidents_info = intro_message
        for siem_incident in incidents:
            new_incidents_info += f"<b>{siem_incident['key']}</b>\n" \
                                  f"Тип: {siem_incident['type']}\n" \
                                  f"Имя: {siem_incident['name']}\n" \
                                  f"Уровень угрозы: ({IncidentSeverity[siem_incident['severity']].value})\n\n"
        users, _ = await get_users(session=session)
        for user in users:
            if user.online_session.online:
                await bot.send_message(chat_id=user.user_id, text=new_incidents_info)
            else:
                await bot.send_message(chat_id=user.user_id,
                                       text=intro_message + 'Авторизуйтесь с помощью /login, чтобы увидеть их.')

        if config.web_app.api_url:
            incidents_json = [
                {
                    "incident_id": incident['id'],
                    "key": incident['key'],
                    "name": incident['name'],
                    "status": IncidentStatus[incident['status']].value,
                    "type": incident['type'],
                    "created_at": parse_iso_datetime(incident['created']).isoformat(),
                    "severity": IncidentSeverity[incident['severity']].value
                } for incident in incidents
            ]

            await web_app.submit_new_incidents_to_server(incidents=incidents_json)

        return await bot.send_message(chat_id=config.settings.admin_id, text=new_incidents_info)
