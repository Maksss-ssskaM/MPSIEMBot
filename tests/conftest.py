import asyncio
from unittest.mock import MagicMock

import pytest_asyncio
from aiogram import Dispatcher, Router, Bot
from aiogram.fsm.strategy import FSMStrategy
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from database.db_settings import SQLALCHEMY_DATABASE_URL, Base, get_redis_storage
from handlers import main_router
from mocked_bot import MockedBot
from mocked_data import UserFactory, OnlineSessionFactory, SettingsFactory


@pytest_asyncio.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture()
def dispatcher():
    storage = get_redis_storage()
    fsm_strategy = FSMStrategy.CHAT
    event_isolation = None

    dp = Dispatcher(
        storage=storage, fsm_strategy=fsm_strategy, events_isolation=event_isolation
    )

    def register_handlers(router: Router, dispatcher: Dispatcher):
        for handler in router.message.handlers:
            callback_values = [filter_.callback for filter_ in handler.filters]
            dispatcher.message.register(handler.callback, *callback_values)

        for handler in router.callback_query.handlers:
            callback_values = [filter_.callback for filter_ in handler.filters]
            dispatcher.callback_query.register(handler.callback, *callback_values)

        sub_routers = router.sub_routers
        if sub_routers:
            for subrouter in sub_routers:
                register_handlers(subrouter, dispatcher)

    register_handlers(router=main_router.router, dispatcher=dp)

    return dp


@pytest_asyncio.fixture()
async def session():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    connection = await engine.connect()
    trans = await connection.begin()

    Session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)
    session = Session()

    deletion = session.delete

    async def mock_delete(instance):
        insp = inspect(instance)
        if not insp.persistent:
            session.expunge(instance)
        else:
            await deletion(instance)

        return await asyncio.sleep(0)

    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
        await engine.dispose()


@pytest_asyncio.fixture()
async def scheduler(bot: Bot, session: AsyncSession):
    session_maker = async_sessionmaker(bind=session.bind)

    jobstores = {
        'default': RedisJobStore(
            jobs_key='mocked_jobs', run_times_key='mocked_run_times',
            host='localhost', db=2, port=6379
        )
    }

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(session_maker, declared_class=async_sessionmaker)

    scheduler.start()

    yield scheduler

    scheduler.shutdown()


@pytest_asyncio.fixture(autouse=True)
def setup_factories(session: AsyncSession):
    UserFactory.session = session
    OnlineSessionFactory.session = session
    SettingsFactory.session = session
