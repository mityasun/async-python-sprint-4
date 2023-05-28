from models.short_url import ShortUrl as ShortUrlModel
from models.short_url import ShortUrlHistory
from schemas.short_url import OriginalUrl, ShortUrl

from .base import RepositoryDB


class Repository(
    RepositoryDB[ShortUrlModel, ShortUrlHistory, ShortUrl, OriginalUrl]
):
    pass


urls_crud = Repository(ShortUrlModel, ShortUrlHistory)
