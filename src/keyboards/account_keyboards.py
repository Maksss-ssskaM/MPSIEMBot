from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicons import ACCOUNT_LEXICON


def create_user_account_kb(*buttons: str, width: int = 1) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    kb_builder.row(*[InlineKeyboardButton(
        text=ACCOUNT_LEXICON['menu'][button] if button in ACCOUNT_LEXICON['menu'] else button,
        callback_data=button) for button in buttons], width=width)

    return kb_builder.as_markup()


def create_confirm_new_password_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Подтвердить',
                callback_data='confirm_new_password'
            )],
            [InlineKeyboardButton(
                text='Отклонить',
                callback_data='change_password'
            )]
        ])
