from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from services import user_service
from .operations import user_operations
from .user_info import user_info

router = Router()
router.include_routers(user_operations.router, user_info.router)


@router.callback_query(F.data == 'users_right')
async def process_right_user_list(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    current_page = data.get('user_list_current_page') + 1

    users_info, reply_markup = await user_service.display_users_in_list(
        session=session,
        state=state,
        current_page=current_page,
        users_per_page=5
    )

    return await callback.message.edit_text(text=users_info, reply_markup=reply_markup)


@router.callback_query(F.data == 'users_left')
async def process_left_user_list(callback: CallbackQuery, session: AsyncSession, state: FSMContext):

    data = await state.get_data()
    current_page = data.get('user_list_current_page')

    if current_page > 0:
        current_page -= 1

    users_info, reply_markup = await user_service.display_users_in_list(
        session=session,
        state=state,
        current_page=current_page,
        users_per_page=5
    )

    return await callback.message.edit_text(text=users_info, reply_markup=reply_markup)
