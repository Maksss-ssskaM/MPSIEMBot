from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from config_data import load_config
from database.models.user import User, OnlineSession

config = load_config()


class IsAdmin(BaseFilter):
    async def __call__(self, update: Message | CallbackQuery) -> bool:
        return update.from_user.id == config.settings.admin_id


class IsRegistered(BaseFilter):
    async def __call__(self, update: Message | CallbackQuery, session: AsyncSession) -> bool:
        user = await session.get(User, update.from_user.id)
        return bool(user) or update.from_user.id == config.settings.admin_id


class IsAuthorized(BaseFilter):
    async def __call__(self, update: Message | CallbackQuery, session: AsyncSession) -> bool:
        user_id = update.from_user.id
        if user_id == config.settings.admin_id:
            return True

        online_session = await session.get(OnlineSession, user_id)
        return online_session and online_session.online


