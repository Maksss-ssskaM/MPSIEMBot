import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from database import User, OnlineSession, get_session_maker
from database.query_service import get_user, get_online_session_by_user_id, get_expired_online_sessions
from services import scheduler_service
from argon2 import PasswordHasher

password_hasher = PasswordHasher()


async def register_user(user_id: int, username: str, session: AsyncSession) -> None:
    session.add(User(user_id=user_id, username=username))
    session.add(OnlineSession(user_id=user_id))
    await session.commit()


async def create_password(user_id: int, session: AsyncSession, new_password: Optional[str] = None) -> str:
    user = await get_user(user_id=user_id, session=session)
    if not new_password:
        new_password = generate_random_string()
    hashed_reg_pass = password_hasher.hash(new_password)
    user.password = hashed_reg_pass
    await session.commit()
    return new_password


async def login_user(user_id: int, session: AsyncSession, scheduler: AsyncIOScheduler) -> None:
    user = await get_user(user_id=user_id, session=session)
    user_session = user.online_session
    run_date = datetime.now() + timedelta(hours=24)

    job = scheduler.add_job(
        scheduler_service.expired_online_session_timer,
        trigger='date',
        run_date=run_date,
        kwargs={'user_id': user_id}
    )

    user_session.online = True
    user_session.expire_at = run_date
    user_session.scheduler_id = job.id

    await session.commit()


async def logout_user(user_id: int, session: AsyncSession, scheduler: AsyncIOScheduler) -> None:
    online_session = await get_online_session_by_user_id(session=session, user_id=user_id)
    if job_id := online_session.scheduler_id:
        scheduler.remove_job(job_id=job_id)

    online_session.online = False
    online_session.expire_at = online_session.scheduler_id = None
    await session.commit()


async def close_expired_sessions(bot: Bot) -> None:
    session_maker = get_session_maker()
    async with session_maker() as session:
        online_sessions = await get_expired_online_sessions(session=session)
        for online_session in online_sessions:
            user_id = online_session.user_id
            await scheduler_service.expired_online_session_timer(bot=bot, user_id=user_id)


def generate_random_string(length: int = 10) -> str:
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string


def is_valid_password(password: str) -> bool:
    return (8 <= len(password) <= 127 and
            any(char.isdigit() for char in password) and
            any(char.isalpha() for char in password))
