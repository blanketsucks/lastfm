from __future__ import annotations

from typing import Dict, Any, List, Optional, TYPE_CHECKING

from .http import HTTPClient
from .tag import Tag
from .artist import Artist

if TYPE_CHECKING:
    from .album import Album

__all__ = 'Track',

class Track:
    __slots__ = (
        '_http',
        '_data',
        'name',
        'mbid',
        'url',
        'duration',
        'listeners',
        'playcount',
    )

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        self.name: str = data['name']
        self.url: str = data['url']
        self.mbid: Optional[str] = data.get('mbid')
        self.duration: int = data['duration'] if 'duration' in data else 0

        if 'stats' in data:
            self.listeners: int = int(data['stats']['listeners'])
            self.playcount: int = int(data['stats']['playcount'])
        else:
            self.listeners = int(data.get('listeners', 0))
            self.playcount = int(data.get('playcount', 0))

    def __repr__(self) -> str:
        return f'<Track name={self.name!r}>'

    @property
    def toptags(self) -> List[Tag]:
        if 'toptags' not in self._data:
            return []

        return [Tag(tag, self._http) for tag in self._data['toptags']['tag']]

    @property
    def artist(self) -> Optional[Artist]:
        if 'artist' not in self._data:
            return None

        return Artist(self._data['artist'], self._http)

    @property
    def album(self) -> Optional[Album]:
        from .album import Album

        if 'album' not in self._data:
            return None

        return Album(self._data['album'], self._http)

    @property
    def attr(self) -> Dict[str, Any]:
        return self._data.get('@attr', {})

    def is_now_playing(self) -> bool:
        nowplaying = self.attr.get('nowplaying', False)
        if isinstance(nowplaying, str):
            return nowplaying.lower() == 'true'
        
        return nowplaying

    async def get_album(self) -> Optional[Album]:
        from .album import Album

        if not self.artist or not self.album:
            return None

        data = await self._http.get_album_info(self.artist.name, self.album.name)
        return Album(data['album'], self._http)

    async def get_artist(self) -> Optional[Artist]:
        if not self.artist:
            return None

        data = await self._http.get_artist_info(self.artist.name)
        return Artist(data['artist'], self._http)

    async def get_tags(self) -> List[Tag]:
        if not self.artist:
            return []

        data = await self._http.get_track_tags(self.artist.name, self.name)
        return [Tag(tag, self._http) for tag in data['tags']['tag']]

    async def get_top_tags(self) -> List[Tag]:
        if not self.artist:
            return []

        data = await self._http.get_track_top_tags(self.artist.name, self.name)
        return [Tag(tag, self._http) for tag in data['toptags']['tag']]

    async def add_tags(self, api_sig: str, sk: str, *tags: str) -> None:
        if len(tags) > 10:
            raise ValueError('Cannot add more than 10 tags')
        
        if not self.artist:
            return None

        await self._http.add_track_tags(api_sig, sk, self.artist.name, self.name, tags)

    async def remove_tag(self, api_sig: str, sk: str, tag: str) -> None:
        if not self.artist:
            return None
    
        await self._http.remove_track_tag(api_sig, sk, self.artist.name, self.name, tag)

    async def love(self, api_sig: str, sk: str) -> None:
        if not self.artist:
            return None

        await self._http.love_track(api_sig, sk, self.artist.name, self.name)

    async def unlove(self, api_sig: str, sk: str) -> None:
        if not self.artist:
            return None

        await self._http.unlove_track(api_sig, sk, self.artist.name, self.name)