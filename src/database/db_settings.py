from asyncio import current_task

from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config_data import load_config

config = load_config()

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://' \
                          f'{config.db.db_user}:' \
                          f'{config.db.db_pass}@' \
                          f'{config.db.db_host}:' \
                          f'{config.db.db_port}/' \
                          f'{config.db.db_name}'

async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True)


def get_session_maker():
    return async_scoped_session(sessionmaker(async_engine, class_=AsyncSession), scopefunc=current_task)


redis_settings = {'host': config.redis.redis_host, 'db': 2, 'port': 6379}


def get_redis_storage():
    return RedisStorage(redis=Redis(**redis_settings))


def get_redis_jobstore():
    return RedisJobStore(
        jobs_key='scheduled_jobs',
        run_times_key='scheduled_jobs_running',
        **redis_settings
    )


Base = declarative_base()
