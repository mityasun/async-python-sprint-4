import os
from logging import config as logging_config

from pydantic import BaseSettings
from pydantic.fields import Field
from pydantic.networks import PostgresDsn

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):

    app_title: str = 'Link shortening service'
    tag_db_status = 'Database status'
    tag_urls_short = 'Shorted Links'
    database_dsn: PostgresDsn = Field(
        'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres',
        env='DATABASE_DSN'
    )
    project_host: str = Field('127.0.0.1', env='PROJECT_HOST')
    project_port: int = Field(8000, env='PROJECT_PORT')
    engine_echo: bool = Field(False, env='ENGINE_ECHO')
    short_url_length: int = 8
    black_list: list[str] = [
        # '111.222.333.444',
    ]

    class Config:
        env_file = '.env'


app_settings = AppSettings()
