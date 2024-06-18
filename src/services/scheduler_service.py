from aiogram import Bot
from database import get_session_maker
from lexicons import AUTH_LEXICON
from database.query_service import get_user


async def expired_online_session_timer(user_id: int, bot: Bot) -> None:
    session_maker = get_session_maker()
    async with session_maker() as session:
        user = await get_user(user_id=user_id, session=session)
        user_session = user.online_session
        user_session.online = False
        user_session.expire_at = user_session.scheduler_id = None

        await session.commit()
        await bot.send_message(chat_id=user_id, text=AUTH_LEXICON['logout']['session_expired'])
