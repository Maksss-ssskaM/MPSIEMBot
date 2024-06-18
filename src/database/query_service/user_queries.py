from typing import Sequence, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config_data import load_config
from database import User, OnlineSession

config = load_config()


async def get_user(session: AsyncSession, user_id: int) -> User:
    query = select(User).where(User.user_id == user_id).options(selectinload(User.online_session))
    result = await session.execute(query)

    return result.scalar()


async def get_users(session: AsyncSession, skip: int = 0, limit: int = 100) -> Tuple[Sequence[User], int]:
    users_query = (select(User)
                   .filter(User.user_id != config.settings.admin_id)
                   .options(selectinload(User.online_session))
                   .join(User.online_session)
                   .order_by(OnlineSession.online.desc())
                   .offset(skip).limit(limit))

    count_query = select(func.count()).select_from(
        select(User).filter(User.user_id != config.settings.admin_id).subquery())

    users_result = await session.execute(users_query)
    count_result = await session.execute(count_query)

    users = users_result.scalars().all()
    users_count = count_result.scalar_one()

    return users, users_count
