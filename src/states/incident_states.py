from aiogram.fsm.state import StatesGroup, State


class FSMIncidents(StatesGroup):
    get_incident_id = State()


class FSMUpdateIncident(StatesGroup):
    waiting_for_name = State()
    waiting_for_status = State()
    waiting_for_severity = State()