from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database import Settings, get_session_maker
from database.query_service import get_settings
from services.auth_service import generate_random_string, password_hasher


async def set_initial_values() -> None:
    session_maker = get_session_maker()
    async with session_maker() as session:
        settings = await get_settings(session=session)
        if settings:
            SettingsHandler.pause_time = settings.pause_time
            SettingsHandler.time_zone = settings.time_zone
            SettingsHandler.reg_pass = settings.reg_pass
            SettingsHandler.last_incident_time = settings.last_incident_time
        else:
            await SettingsHandler.init_bot(session=session)


class SettingsHandler:
    pause_time: Optional[int] = None
    time_zone: Optional[int] = None
    reg_pass: Optional[str] = None
    last_incident_time: Optional[datetime] = None

    @classmethod
    async def init_bot(cls, session: AsyncSession) -> str:
        reg_pass = generate_random_string()
        hashed_reg_pass = password_hasher.hash(reg_pass)
        settings = Settings(reg_pass=hashed_reg_pass)
        session.add(settings)
        await session.flush()

        cls.reg_pass = hashed_reg_pass
        cls.time_zone = settings.time_zone
        cls.pause_time = settings.pause_time
        await session.commit()
        return reg_pass

    @classmethod
    async def new_reg_pass(cls, session: AsyncSession) -> str:
        reg_pass = generate_random_string()
        hashed_reg_pass = password_hasher.hash(reg_pass)
        settings = await get_settings(session=session)
        settings.reg_pass = cls.reg_pass = hashed_reg_pass
        await session.commit()
        return reg_pass

    @classmethod
    async def new_time_zone(cls, new_time_zone: int, session: AsyncSession) -> None:
        settings = await get_settings(session=session)
        settings.time_zone = cls.time_zone = new_time_zone
        await session.commit()

    @classmethod
    async def new_pause_time(cls, new_pause_time: int, session: AsyncSession) -> None:
        settings = await get_settings(session=session)
        settings.pause_time = cls.pause_time = new_pause_time
        await session.commit()
