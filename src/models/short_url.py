from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from db.db import Base


class ShortUrl(Base):
    """Short url model."""

    __tablename__ = 'short_url'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    original_url = Column(URLType, nullable=False)
    short_id = Column(String(8), index=True, nullable=False)
    short_url = Column(URLType, nullable=False)
    usage_count = Column(Integer)
    url_history = relationship('ShortUrlHistory', cascade="all, delete")
    del_status = Column(Boolean, default=False)


class ShortUrlHistory(Base):
    """Url usage history model."""

    __tablename__ = 'short_url_history'
    id = Column(Integer, primary_key=True)
    short_url = Column(
        Integer, ForeignKey('short_url.id', ondelete="CASCADE"), nullable=False
    )
    user_agent = Column(String(50), nullable=False)
    used_at = Column(DateTime, index=True, default=datetime.utcnow)
