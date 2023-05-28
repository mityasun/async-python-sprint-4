import logging
from logging import config as logging_config
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.mixins import object_is_exist, object_is_deleted
from core.config import app_settings
from core.logger import LOGGING
from db.db import get_session
from schemas.short_url import (OriginalUrl, OriginalUrlsList,
                               ShortUrl, ShortUrlsList)
from services.short_url import urls_crud

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    '/ping', status_code=status.HTTP_200_OK,
    tags=[app_settings.tag_db_status],
    description='Return database availability status.'
)
async def health_db(db: AsyncSession = Depends(get_session)) -> Any:
    """Database availability status"""

    db_status = await urls_crud.ping_db(db=db)
    logger.info('Get db status')
    return {'database_connection': db_status}


@router.get(
    '/', status_code=status.HTTP_200_OK,
    tags=[app_settings.tag_urls_short], description='API version'
)
async def api_version() -> Any:
    """Get API version."""

    logger.info('Get API version')
    return {'version': 'v1'}


@router.post(
    '/', status_code=status.HTTP_201_CREATED,
    response_model=ShortUrl, response_model_exclude={'del_status'},
    tags=[app_settings.tag_urls_short], description='Create short url.'
)
async def create_short_url(
    original_url: OriginalUrl, db: AsyncSession = Depends(get_session)
) -> Any:

    """Create short url"""

    obj = await urls_crud.create(db=db, obj_in=original_url)
    logger.info(f'Short url created {obj.original_url} -> {obj.short_id}')
    return obj


@router.post(
    '/shorten', status_code=status.HTTP_201_CREATED,
    response_model=ShortUrlsList,
    tags=[app_settings.tag_urls_short], description='Bulk create short urls.'
)
async def bulk_create_short_urls(
        list_urls: OriginalUrlsList, db: AsyncSession = Depends(get_session)
) -> Any:
    """Bulk create short urls"""

    logger.info(f'Bulk created short urls: {list_urls}')
    return await urls_crud.bulk_create(db=db, obj_in=list_urls)


@router.get(
    '/{short_id}', status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_model=OriginalUrl, tags=[app_settings.tag_urls_short],
    description='Return original url bu uuid.'
)
async def get_url(
    short_id: str, db: AsyncSession = Depends(get_session),
    user_agent: Optional[str] = Header(None)
) -> Any:
    """Return original url by id."""

    obj = await urls_crud.get(db=db, short_id=short_id)
    object_is_exist(obj)
    object_is_deleted(obj)
    logger.info(f'Get original url with id: {obj.short_id}')
    await urls_crud.update_usage_count(db=db, db_obj=obj)
    logger.info(f'Update usage count for id: {obj.short_id}')
    await urls_crud.create_history(
        db=db, short_id=obj.id, user_agent=user_agent
    )
    logger.info(f'Create usage history for id: {obj.short_id}')
    return obj


@router.get(
    '/{short_id}/status', status_code=status.HTTP_200_OK,
    tags=[app_settings.tag_urls_short], description='Get url usage history.'
)
async def get_url_status(
    short_id: str,
    full_info: bool = Query(default=False, alias='full-info'),
    max_result: int = Query(
        default=10, ge=1, alias='max-result', description='Query max size.'
    ),
    offset: int = Query(default=0, ge=0, description='Query offset.'),
    db: AsyncSession = Depends(get_session),
) -> Any:
    """Get url usage history."""

    obj = await urls_crud.get(db=db, short_id=short_id)
    object_is_exist(obj)
    object_is_deleted(obj)
    result = await urls_crud.get_status(
        db=db, db_obj=obj, full_info=full_info, limit=max_result, offset=offset
    )
    if not full_info:
        logger.info(f'Return count usage for url with id: {obj.short_id}')
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={'usage_count': result}
        )
    logger.info(f'Return usage history for url with id: {obj.short_id}')
    return result


@router.delete(
    '/{short_id}', status_code=status.HTTP_200_OK,
    tags=[app_settings.tag_urls_short], description='Delete short url by uuid.'
)
async def delete_url(
    short_id: str, db: AsyncSession = Depends(get_session)
) -> Any:
    """Delete short url by id."""

    obj = await urls_crud.get(db=db, short_id=short_id)
    object_is_exist(obj)
    object_is_deleted(obj)
    await urls_crud.delete(db=db, db_obj=obj)
    logger.info(f'Set del_status to id: {obj.short_id}')
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={'url_delete': f'Short url {obj.short_id} was deleted'}
    )
