from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def back_kb(button: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data=button)]])


def delete_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[]])
