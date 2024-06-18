from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import OnlineSession


async def get_expired_online_sessions(session: AsyncSession) -> Sequence[OnlineSession]:
    query = select(OnlineSession).where(OnlineSession.expire_at < datetime.now())
    result = await session.execute(query)

    return result.scalars().all()


async def get_online_session_by_user_id(session: AsyncSession, user_id: int) -> OnlineSession:
    query = select(OnlineSession).where(OnlineSession.user_id == user_id)
    result = await session.execute(query)

    return result.scalar()