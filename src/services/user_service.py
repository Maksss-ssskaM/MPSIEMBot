from datetime import datetime
from math import ceil

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from database import User, OnlineSession
from keyboards import create_user_list_kb
from database.query_service import get_users, get_user


def get_user_info(user: User, online_session: OnlineSession) -> str:
    session_status = 'Онлайн ✅' if online_session.online else 'Оффлайн ❌'

    if online_session.expire_at:
        session_time_left = online_session.expire_at - datetime.now()
        hours, _ = divmod(session_time_left.seconds, 3600)
        formatted_session_time_left = f'({int(hours)}ч ост.)' if hours > 0 else 'менее часа ост.'
    else:
        formatted_session_time_left = ''

    return f'————————————————————\n' \
           f'<b>{user.username}</b>\n' \
           f'————————————————————\n' \
           f'<b>ID:</b> {user.user_id}\n' \
           f'<b>Статус:</b> {session_status} {formatted_session_time_left}\n\n\n'


async def display_users_in_list(session: AsyncSession, state: FSMContext, current_page: int, users_per_page: int) -> tuple[str, InlineKeyboardMarkup]:
    if current_page < 0 or users_per_page <= 0:
        raise ValueError("Некорректные значения current_page и users_per_page")

    skip = current_page * users_per_page
    users, total_users_count = await get_users(session=session, skip=skip, limit=users_per_page)

    total_pages = ceil(total_users_count / users_per_page)
    await state.update_data(user_list_current_page=current_page, total_pages=total_pages)

    if total_pages > 1:
        if current_page == 0:
            reply_markup = create_user_list_kb('users_right', users=users)
        elif current_page == total_pages - 1:
            reply_markup = create_user_list_kb('users_left', users=users)
        else:
            reply_markup = create_user_list_kb('users_left', 'users_right', users=users)
    else:
        reply_markup = create_user_list_kb(users=users) if total_pages == 1 else None

    users_info = ''.join([get_user_info(user, user.online_session) for user in users]) if users else '⚠️ Список пользователей пуст!'

    return users_info, reply_markup


async def delete_user(user_id: int, session: AsyncSession) -> None:
    user = await get_user(session, user_id)

    if user is None:
        raise ValueError(f"Пользователя с ID {user_id} не существует.")

    online_session = user.online_session
    await session.delete(online_session)
    await session.delete(user)
    await session.commit()
