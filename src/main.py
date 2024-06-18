import asyncio
from aiogram import Bot, Dispatcher

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from sqlalchemy.ext.asyncio import async_sessionmaker

from config_data.config import load_config
from database import get_session_maker, get_redis_storage, get_redis_jobstore
from handlers import main_router
from middlewares import DbSessionMiddleware, SchedulerMiddleware
from services import auth_service
from services.settings_service import set_initial_values


async def main():
    config = load_config()

    session_maker = get_session_maker()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=get_redis_storage())

    jobstores = {'default': get_redis_jobstore()}
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Europe/Moscow', jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(session_maker, declared_class=async_sessionmaker)
    await auth_service.close_expired_sessions(bot=bot)
    await set_initial_values()
    scheduler.start()

    dp.update.middleware.register(DbSessionMiddleware(session_pool=session_maker))
    dp.update.middleware.register(SchedulerMiddleware(scheduler=scheduler))

    dp.include_router(main_router.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
