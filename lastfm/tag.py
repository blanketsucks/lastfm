from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, Optional, List

from .chart import WeeklyChart
from .http import HTTPClient
from .wiki import Wiki

if TYPE_CHECKING:
    from .track import Track
    from .album import Album
    from .artist import Artist

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
    
    async def get_similar(self) -> List[Tag]:
        data = await self._http.get_tag_similar(self.name)
        return [Tag(tag, self._http) for tag in data['similartags']['tag']]
    
    async def get_top_artists(
        self, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Artist]:
        from .artist import Artist

        data = await self._http.get_tag_top_artists(self.name, limit, page)
        return [Artist(artist, self._http) for artist in data['topartists']['artist']]
    
    async def get_top_tracks(
        self, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Track]:
        from .track import Track

        data = await self._http.get_tag_top_tracks(self.name, limit, page)
        print(data.keys())
        return [Track(track, self._http) for track in data['tracks']['track']]
    
    async def get_top_albums(
        self, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Album]:
        from .album import Album

        data = await self._http.get_tag_top_albums(self.name, limit, page)
        return [Album(album, self._http) for album in data['albums']['album']]
    
    async def get_weekly_chart_list(self) -> List[WeeklyChart]:
        data = await self._http.get_tag_weekly_chart_list(self.name)
        return [WeeklyChart.from_dict(chart) for chart in data['weeklychartlist']['chart']]