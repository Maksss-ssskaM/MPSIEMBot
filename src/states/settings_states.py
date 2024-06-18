from aiogram.fsm.state import StatesGroup, State


class FSMNewParameter(StatesGroup):
    new_pause_time = State()
    new_time_zone = State()