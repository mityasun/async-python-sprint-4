from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ShortUrl(BaseModel):
    """Short url"""

    short_id: str
    short_url: HttpUrl

    class Config:
        orm_mode = True


class ShortUrlsList(BaseModel):
    """List short urls"""

    __root__: list[ShortUrl]


class UrlHistoryShortInfo(BaseModel):
    """Number of times the url is used"""

    usage_count: int

    class Config:
        orm_mode = True


class UrlHistoryInfo(BaseModel):
    """Url usage history"""

    user_agent: str
    used_at: datetime

    class Config:
        orm_mode = True


class UrlHistoryFullInfo(BaseModel):
    """Urls usage history"""

    __root__: list[UrlHistoryInfo]


class OriginalUrl(BaseModel):
    """Original url"""

    original_url: HttpUrl

    class Config:
        orm_mode = True


class OriginalUrlsList(BaseModel):
    """List of url for bulk create"""

    __root__: list[OriginalUrl]
