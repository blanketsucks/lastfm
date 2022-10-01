from typing import Dict, Any, Optional

from .http import HTTPClient
from .wiki import Wiki

__all__ = 'Tag',

class Tag:
    __slots__ = ('_data', '_http', 'name', 'url', 'total', 'reach')

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        self.name: str = data['name']
        self.url: Optional[str] = data.get('url')

        self.total: int = data.get('total', 0)
        self.reach: int = data.get('reach', 0)

    def __repr__(self) -> str:
        return f'<Tag name={self.name!r}>'

    @property
    def wiki(self) -> Optional[Wiki]:
        wiki = self._data.get('wiki')
        if not wiki:
            return None
        
        return Wiki(wiki)