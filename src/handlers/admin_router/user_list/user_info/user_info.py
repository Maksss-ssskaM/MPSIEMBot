from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import create_user_info_kb, UsersListActions
from database.query_service import get_user
from services import user_service

router = Router()


@router.callback_query(UsersListActions.filter(F.action == 'user_info'))
async def get_user_info(callback: CallbackQuery, session: AsyncSession, callback_data: UsersListActions):
    user = await get_user(session=session, user_id=callback_data.user_id)
    online_session = user.online_session
    buttons = ['generate_new_password', 'delete_user', 'back_to_user_list']

    if online_session.online:
        buttons.insert(0, 'close_session')

    user_info = user_service.get_user_info(user=user, online_session=online_session)
    return await callback.message.edit_text(
        text=user_info,
        reply_markup=create_user_info_kb(*buttons, user_id=user.user_id, username=user.username)
    )


@router.callback_query(UsersListActions.filter(F.action == 'back_to_user_list'))
async def back_to_user_list(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    list_data = await state.get_data()
    users_info, reply_markup = await user_service.display_users_in_list(
        session=session,
        state=state,
        current_page=list_data['user_list_current_page'],
        users_per_page=5
    )

    return await callback.message.edit_text(text=users_info, reply_markup=reply_markup)
