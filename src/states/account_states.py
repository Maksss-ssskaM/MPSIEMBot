from aiogram.fsm.state import StatesGroup, State


class FSMAccount(StatesGroup):
    get_new_password = State()
    confirm_password = State()
