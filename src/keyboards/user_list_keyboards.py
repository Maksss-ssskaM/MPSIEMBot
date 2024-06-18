from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.models.user import User
from lexicons import MENU_LEXICON, USER_LIST_LEXICON, PAGINATION_LEXICON


class UsersListActions(CallbackData, prefix='user_list'):
    action: str
    user_id: int
    username: str


def create_main_menu(*buttons: str, width: int = 1) -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()

    kb_builder.row(*[KeyboardButton(
        text=MENU_LEXICON[button] if button in MENU_LEXICON else button) for button in buttons]
                   )
    kb_builder.adjust(width)
    return kb_builder.as_markup(resize_keyboard=True)


def create_user_list_kb(*buttons: str, users: Sequence[User]) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    pagination_buttons = [InlineKeyboardButton(
        text=PAGINATION_LEXICON[button] if button in PAGINATION_LEXICON else button, callback_data=button) for button in
        buttons]

    users_buttons = [InlineKeyboardButton(
        text=user.username, callback_data=UsersListActions(
            action='user_info', user_id=user.user_id, username=user.username).pack()
    ) for user in users]

    if pagination_buttons:
        kb_builder.row(*pagination_buttons, width=len(pagination_buttons))

    kb_builder.row(*users_buttons, width=2)

    return kb_builder.as_markup()


def create_user_info_kb(*buttons: str, user_id: int, username: str, width: int = 1) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(*[InlineKeyboardButton(
        text=USER_LIST_LEXICON['user_info_kb'][button] if button in USER_LIST_LEXICON['user_info_kb'] else button,
        callback_data=UsersListActions(
            action=button,
            user_id=user_id,
            username=username
        ).pack()) for button in buttons])

    kb_builder.row()

    kb_builder.adjust(width)
    return kb_builder.as_markup(resize_keyboard=True)


def confirm_reject_user_deletion_kb(user_id: int, username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Подтверить', callback_data=UsersListActions(
            action='confirm_user_deletion', user_id=user_id, username=username).pack()),
         InlineKeyboardButton(text='Отклонить', callback_data=UsersListActions(
            action='user_info', user_id=user_id, username=username).pack())
         ],
    ])
