import logging
from abc import ABC, abstractmethod
from logging import config as logging_config
from typing import Any, Generic, Optional, Type, TypeVar

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from shortuuid import ShortUUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import app_settings
from core.logger import LOGGING
from db.db import Base
from models.short_url import ShortUrl
from schemas.short_url import UrlHistoryInfo

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
BulkCreateSchemaType = TypeVar("BulkCreateSchemaType", bound=BaseModel)


def create_short_url(url_len: int) -> str:

    return ShortUUID().random(length=url_len)


def create_obj(obj_in_data, model) -> ShortUrl:

    add_obj_info = {}
    short_id = create_short_url(app_settings.short_url_length)
    add_obj_info['short_id'] = short_id
    short_url = (
        f'http://{app_settings.project_host}:'
        f'{app_settings.project_port}/api/v1/{short_id}'
    )
    add_obj_info['short_url'] = short_url
    add_obj_info['usage_count'] = 0
    obj_in_data.update(add_obj_info)
    return model(**obj_in_data)


class Repository(ABC):

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def create_history(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_status(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def bulk_create(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def ping_db(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update_usage_count(self, *args, **kwargs):
        raise NotImplementedError


class RepositoryDB(
    Repository,
    Generic[
        ModelType, CreateSchemaType, UpdateSchemaType, BulkCreateSchemaType
    ]
):
    def __init__(self, model: Type[ModelType], request: Type[ModelType]):
        self._model = model
        self._request_model = request

    async def ping_db(self, db: AsyncSession) -> bool:
        """Get database availability status"""

        result = await db.execute(statement=select(self._model))
        return True if result else False

    async def create(
            self, db: AsyncSession, *, obj_in: CreateSchemaType
    ) -> ModelType:
        """Create short url"""

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = create_obj(obj_in_data, self._model)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def bulk_create(
            self, db: AsyncSession, obj_in: BulkCreateSchemaType
    ) -> list[ModelType]:
        """Bulk create short urls"""

        list_urls = jsonable_encoder(obj_in)
        db_obj = [create_obj(data, self._model) for data in list_urls]
        db.add_all(db_obj)
        await db.commit()
        for obj in db_obj:
            await db.refresh(obj)
        return db_obj

    async def delete(
            self, db: AsyncSession, db_obj: ModelType
    ) -> None:
        """Set delete status to short url"""

        db_obj.del_status = True
        await db.commit()
        await db.refresh(db_obj)

    async def get(
            self, db: AsyncSession, short_id: Any
    ) -> Optional[ModelType]:
        """Get original url."""

        statement = select(self._model).where(self._model.short_id == short_id)
        result = await db.execute(statement=statement)
        obj = result.scalar_one_or_none()
        if not obj:
            logger.info('Short url not found')
            raise HTTPException(status_code=400, detail='Short url not found')
        if obj.del_status:
            logger.info('Short url was deleted')
            raise HTTPException(
                status_code=400, detail='Short url was deleted'
            )
        return obj

    async def update_usage_count(
            self, db: AsyncSession, db_obj: ModelType
    ) -> None:
        """Update usage count"""

        db_obj.usage_count += 1
        await db.commit()
        await db.refresh(db_obj)

    async def create_history(
            self, db: AsyncSession, short_id: int, user_agent: str
    ) -> None:
        """Create usage history"""

        request_obj = self._request_model(
            short_url=short_id, user_agent=user_agent
        )
        db.add(request_obj)
        await db.commit()
        await db.refresh(request_obj)

    async def get_status(
            self, db: AsyncSession, db_obj: ModelType,
            full_info: bool, limit: int, offset: int
    ) -> list[UrlHistoryInfo]:
        """Get usage count of usage history"""

        if not full_info:
            return db_obj.usage_count
        statement = select(
            self._request_model
        ).where(
            self._request_model.short_url == db_obj.id
        ).offset(offset).limit(limit)
        result = await db.execute(statement=statement)
        return [
            UrlHistoryInfo.from_orm(item) for item in result.scalars().all()
        ]
