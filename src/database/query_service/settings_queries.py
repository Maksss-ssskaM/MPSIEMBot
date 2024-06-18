from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Settings


async def get_settings(session: AsyncSession) -> Settings:
    query = select(Settings).limit(1)
    result = await session.execute(query)

    return result.scalar()