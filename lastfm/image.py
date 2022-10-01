from typing import Dict, Any

from enum import Enum

from .http import HTTPClient

__all__ = ('ImageSize', 'Image')

class ImageSize(str, Enum):
    Small = 'small'
    Medium = 'medium'
    Large = 'large'
    ExtraLarge = 'extralarge'
    Mega = 'mega'
    Unspecified = ''

class Image:
    __slots__ = ('_http', 'url', 'size')

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http

        self.url: str = data['#text']
        self.size: ImageSize = ImageSize(data['size'])

    def __repr__(self) -> str:
        return f'<Image url={self.url!r} size={self.size!r}>'

    async def read(self) -> bytes:
        if not self.url:
            raise ValueError('Image does not have a URL')

        return await self._http.read(self.url)