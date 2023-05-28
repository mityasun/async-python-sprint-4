import os
from logging import config as logging_config

from dotenv import load_dotenv
from pydantic import BaseSettings
from pydantic.fields import Field
from pydantic.networks import PostgresDsn

from core.logger import LOGGING

load_dotenv('.env')

logging_config.dictConfig(LOGGING)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):

    app_title: str = os.getenv('APP_TITLE', default='default-value')
    tag_db_status = 'Database status'
    tag_urls_short = 'Shorted Links'
    database_dsn: PostgresDsn = Field(
        'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres',
        env='DATABASE_DSN'
    )
    project_host: str = os.getenv('PROJECT_HOST', default='127.0.0.1')
    project_port: int = os.getenv('PROJECT_PORT', default='8000')
    welcome: str = (
        f'Welcome to {app_title}! '
        f'API docs: http://{project_host}:{project_port}/redoc'
    )
    short_url_length: int = 8
    black_list: list[str] = [
        # '111.222.333.444',
    ]

    class Config:
        env_file = '.env'


app_settings = AppSettings()
