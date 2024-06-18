from typing import Sequence, Optional
from uuid import UUID

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.incident import Incident, IncidentStatus, IncidentSeverity
from lexicons import PAGINATION_LEXICON, FILTER_LEXICON


class IncidentsBookActions(CallbackData, prefix='incident_book'):
    action: str
    incident_id: UUID


class UpdateIncidentActions(CallbackData, prefix='update_incident'):
    action: str
    incident_id: UUID


def create_incident_book_kb(*buttons: str, incidents: Sequence[Incident],
                            incidents_per_page: int) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    pagination_buttons = [InlineKeyboardButton(
        text=PAGINATION_LEXICON[button] if button in PAGINATION_LEXICON else button, callback_data=button) for button in
        buttons]

    incidents_buttons = [InlineKeyboardButton(
        text=incident.key, callback_data=IncidentsBookActions(
            action='incident_info', incident_id=incident.incident_id).pack()
    ) for incident in incidents]

    other_buttons = [
        InlineKeyboardButton(text=f'Кол-во: {incidents_per_page}', callback_data='change_incidents_quantity_per_page'),
        InlineKeyboardButton(text='Фильтр 🔎', callback_data='book_filter')
    ]

    kb_builder.row(*pagination_buttons, width=len(pagination_buttons))
    kb_builder.row(*incidents_buttons, width=3)
    kb_builder.row(*other_buttons)

    return kb_builder.as_markup()


async def create_filter_kb(state: Optional[FSMContext] = None):
    book_data = await state.get_data() if state else {'date_sort': 'newest_first', 'severity': None, 'status': None}
    date_sorting = book_data.get('date_sort', 'newest_first')
    severity = book_data.get('severity', None)
    status = book_data.get('status', None)

    severity_filter = severity if severity in FILTER_LEXICON[
        'severity_filter'] else 'default_severity'

    status_filter = status if status in FILTER_LEXICON[
        'status_filter'] else 'default_status'

    keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=FILTER_LEXICON['date_sorting'][date_sorting], callback_data=date_sorting)],
        [InlineKeyboardButton(text=FILTER_LEXICON['severity_filter'][severity_filter], callback_data=severity_filter)],
        [InlineKeyboardButton(text=FILTER_LEXICON['status_filter'][status_filter], callback_data=status_filter)],
        [InlineKeyboardButton(text='Применить', callback_data='apply_filter')]
    ])

    return keyboard_markup


def create_incident_info_kb(incident_id: UUID):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Изменить', callback_data=UpdateIncidentActions(
                action='menu', incident_id=incident_id).pack()),
            InlineKeyboardButton(text='Назад', callback_data='back_to_incident_book')
        ],
    ])


def create_update_incident_kb(incident_id: UUID):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Изменить \"Имя\"', callback_data=UpdateIncidentActions(
                action='name', incident_id=incident_id).pack()),
            InlineKeyboardButton(text='Изменить \"Статус\"', callback_data=UpdateIncidentActions(
                action='status', incident_id=incident_id).pack())
        ],
        [
            InlineKeyboardButton(text='Изменить \"Уровень угрозы\"', callback_data=UpdateIncidentActions(
                action='severity', incident_id=incident_id).pack()),
            InlineKeyboardButton(text='Отмена', callback_data=IncidentsBookActions(
                action='incident_info', incident_id=incident_id).pack())
        ]
    ])


def create_selection_keyboard(action: str, incident_id: UUID):
    kb_builder = InlineKeyboardBuilder()
    if action == 'status':
        for status in IncidentStatus:
            kb_builder.add(InlineKeyboardButton(text=status.value,
                                                callback_data=UpdateIncidentActions(action=status.name,
                                                                                    incident_id=incident_id).pack()))
    elif action == 'severity':
        for severity in IncidentSeverity:
            kb_builder.add(InlineKeyboardButton(text=severity.value,
                                                callback_data=UpdateIncidentActions(action=severity.name,
                                                                                    incident_id=incident_id).pack()))
    kb_builder.adjust(2)
    kb_builder.row(InlineKeyboardButton(text="Отмена", callback_data=IncidentsBookActions(
        action='incident_info', incident_id=incident_id).pack()))
    return kb_builder.as_markup()
