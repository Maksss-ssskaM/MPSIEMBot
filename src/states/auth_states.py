from aiogram.fsm.state import StatesGroup, State


class FSMRegUser(StatesGroup):
    get_password = State()


class FSMLoginUser(StatesGroup):
    get_password = State()