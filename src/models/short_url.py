import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from db.db import Base


class ShortUrl(Base):
    """Short url model."""

    __tablename__ = 'short_url'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    short_url = Column(
        UUID(as_uuid=True), ForeignKey('short_url.id', ondelete="CASCADE"),
        nullable=False,
    )
    user_agent = Column(String(50), nullable=False)
    used_at = Column(DateTime, index=True, default=datetime.utcnow)
