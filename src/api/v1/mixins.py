import logging
from logging import config as logging_config

from fastapi import APIRouter, HTTPException, status

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
router = APIRouter()


def object_is_exist(obj):
    """Check object is exist."""

    if not obj:
        logger.info('Short url not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Short url not found'
        )
    return obj


def object_is_deleted(obj):
    """Check object is deleted."""

    if obj.del_status:
        logger.info('Short url with was deleted')
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail='Short url with was deleted'
        )
    return obj
