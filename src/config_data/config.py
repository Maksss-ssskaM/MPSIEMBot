from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class DatabaseConfig:
    db_user: str
    db_pass: str
    db_host: str
    db_name: str
    db_port: str


@dataclass
class RedisConfig:
    redis_host: str


@dataclass
class WebApp:
    api_url: str | None


@dataclass
class Settings:
    username: str
    password: str
    client_id: str
    client_secret: str
    base_url: str
    admin_id: int


@dataclass
class Config:
    tg_bot: TgBot
    settings: Settings
    db: DatabaseConfig
    redis: RedisConfig
    web_app: WebApp


def load_config():
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(
            token=env('TOKEN')
        ),
        settings=Settings(
            username=env('SIEM_USERNAME'),
            password=env('SIEM_PASSWORD'),
            client_id=env('SIEM_CLIENT_ID'),
            client_secret=env('SIEM_CLIENT_SECRET'),
            base_url=env('SIEM_BASE_URL'),
            admin_id=env.int('ADMIN_ID'),
        ),
        db=DatabaseConfig(
            db_user=env('DB_USER'),
            db_pass=env('DB_PASS'),
            db_host=env('DB_HOST'),
            db_name=env('DB_NAME'),
            db_port=env('DB_PORT')
        ),
        redis=RedisConfig(
            redis_host=env('REDIS_HOST')
        ),
        web_app=WebApp(
            api_url=env('WEB_APP_API_URL', default=None)
        )
    )
