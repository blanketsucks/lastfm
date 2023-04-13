from __future__ import annotations

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import datetime

from .http import HTTPClient
from .tag import Tag
from .artist import Artist

if TYPE_CHECKING:
    from .album import PartialAlbum

__all__ = 'Track',

def to_bool(value: str) -> bool:
    return value == '1'

class Streamable:
    __slots__ = ('fulltrack', 'text')

    def __init__(self, data: Dict[str, Any]) -> None:
        self.fulltrack: bool = to_bool(data['fulltrack'])
        self.text: bool = to_bool(data['#text'])

class Date:
    __slots__ = ('uts', 'text')

    def __init__(self, data: Dict[str, Any]) -> None:
        self.uts: int = int(data['uts'])
        self.text: str = data['#text']

    def __repr__(self) -> str:
        return f'<Date uts={self.uts} text={self.text!r}>'

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.uts)
    
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
        'streamable',
    )

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        self.name: str = data['name']
        self.url: str = data['url']
        self.mbid: Optional[str] = data.get('mbid')
        self.duration: int = data.get('duration', 0)

        stats = data.get('stats')
        if stats is not None:
            self.listeners: int = int(stats['listeners'])
            self.playcount: int = int(stats['playcount'])
        else:
            self.listeners = int(data.get('listeners', 0))
            self.playcount = int(data.get('playcount', 0))

        streamable = data.get('streamable')
        if isinstance(streamable, dict):
            self.streamable = Streamable(streamable)
        elif isinstance(streamable, str):
            self.streamable = Streamable({'fulltrack': streamable, '#text': streamable})
        else:
            self.streamable = Streamable({'fulltrack': '0', '#text': '0'})

    def __repr__(self) -> str:
        return f'<Track name={self.name!r}>'

    @property
    def toptags(self) -> List[Tag]:
        if 'toptags' not in self._data:
            return []

        return [Tag(tag, self._http) for tag in self._data['toptags']['tag']]

    @property
    def artist(self) -> Artist:
        return Artist(self._data['artist'], self._http)

    @property
    def album(self) -> Optional[PartialAlbum]:
        from .album import PartialAlbum

        data = self._data.get('album')
        if data is None:
            return None

        return PartialAlbum(self._data['album'], self.artist.name, self._http)

    @property
    def attr(self) -> Dict[str, Any]:
        return self._data.get('@attr', {})

    async def get_tags(self, *, user: Optional[str] = None) -> List[Tag]:
        if self.mbid:
            data = await self._http.get_track_tags(mbid=self.mbid, user=user)
        else:
            data = await self._http.get_track_tags(self.artist.name, self.name, user=user)

        tags = data['tags'].get('tag')
        if tags is None:
            return []
        
        return [Tag(tag, self._http) for tag in data['tags']['tag']]

    async def get_top_tags(self) -> List[Tag]:
        data = await self._http.get_track_top_tags(self.artist.name, self.name)
        return [Tag(tag, self._http) for tag in data['toptags']['tag']]

    async def add_tags(self, api_sig: str, sk: str, *tags: str) -> None:
        if len(tags) > 10:
            raise ValueError('Cannot add more than 10 tags')
    
        await self._http.add_track_tags(api_sig, sk, self.artist.name, self.name, tags)

    async def remove_tag(self, api_sig: str, sk: str, tag: str) -> None:
        await self._http.remove_track_tag(api_sig, sk, self.artist.name, self.name, tag)

    async def love(self, api_sig: str, sk: str) -> None:
        await self._http.love_track(api_sig, sk, self.artist.name, self.name)

    async def unlove(self, api_sig: str, sk: str) -> None:
        await self._http.unlove_track(api_sig, sk, self.artist.name, self.name)

class UserTrack(Track):
    __slots__ = Track.__slots__ + ('loved',)

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        super().__init__(data, http)

        self.loved: bool = to_bool(data.get('loved', '0'))

    @property
    def date(self) -> Optional[Date]:
        data = self._data.get('date')
        if data is None:
            return None

        return Date(data)

    def is_now_playing(self) -> bool:
        return self.attr.get('nowplaying') == 'true'