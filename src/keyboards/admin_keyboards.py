from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User


class UserRegistrationActions(CallbackData, prefix='registration'):
    action: str
    user_id: int
    username: str


def create_confirm_user_kb(user: User) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подтвердить', callback_data=UserRegistrationActions(
                    action='confirm_reg', user_id=int(user.id), username=user.username).pack()),
                InlineKeyboardButton(text='Отклонить', callback_data=UserRegistrationActions(
                    action='reject_reg', user_id=int(user.id), username=user.username).pack())
            ]
        ]
    )


def create_settings_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Изменить интервал проверки', callback_data='new_pause_time')],
            [InlineKeyboardButton(text='Изменить часовой пояс', callback_data='new_time_zone')],
            [InlineKeyboardButton(text='Создать новый код регистрации', callback_data='new_reg_pass')],
            [InlineKeyboardButton(text='Вкл/Выкл сбор инцидентов', callback_data='launch')]
        ]
    )
