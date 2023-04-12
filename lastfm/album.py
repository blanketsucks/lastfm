from __future__ import annotations

from typing import Dict, Any, List, Optional

from .http import HTTPClient

from .tag import Tag
from .image import Image
from .track import Track
from .wiki import Wiki

__all__ = ('Album', 'PartialAlbum')

def _get_name(data: Dict[str, Any]) -> str:
    if '#text' in data:
        return data['#text']
    elif 'title' in data:
        return data['title']

    raise ValueError('No name found')

class PartialAlbum:
    __slots__ = ('_http', '_data', 'mbid', 'name', 'artist')

    def __init__(self, data: Dict[str, Any], artist: Optional[str], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        mbid = data['mbid']

        self.mbid: Optional[str] = mbid if mbid else None
        self.name: str = _get_name(data)
        self.artist: str = data.get('artist', artist)

    def __repr__(self) -> str:
        return f'<PartialAlbum name={self.name!r} mbid={self.mbid!r}>'
    
    @property
    def images(self) -> List[Image]:
        return [Image(image, self._http) for image in self._data.get('image', [])]
    
    async def fetch(self) -> Album:
        if self.mbid:
            data = await self._http.get_album_info(mbid=self.mbid)
        else:
            data = await self._http.get_album_info(artist=self.artist, album=self.name)

        return Album(data['album'], self._http)

class Album:
    __slots__ = (
        '_http', '_data', 'name', 'artist', 'mbid', 'url', 'listeners', 'playcount'
    )

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        self.name: str = data['name']

        self.artist: Optional[str] = data.get('artist')
        # From what i tested, the mbid is not present if the request was made using an mbid
        self.mbid: Optional[str] = data.get('mbid')
        self.url: Optional[str] = data.get('url')

        self.listeners: int = int(data.get('listeners', 0))
        self.playcount: int = int(data.get('playcount', 0))

    def __repr__(self) -> str:
        return f'<Album name={self.name!r}>'

    @property
    def wiki(self) -> Optional[Wiki]:
        data = self._data.get('wiki')
        if data is None:
            return None

        return Wiki(self._data['wiki'])

    @property
    def images(self) -> List[Image]:
        images = self._data.get('image', [])
        return [Image(image, self._http) for image in images]

    @property
    def tags(self) -> List[Tag]:
        tags = self._data.get('tags', {}).get('tag', [])
        return [Tag(tag, self._http) for tag in tags]

    @property
    def tracks(self) -> List[Track]:
        tracks = self._data.get('tracks', {}).get('track', [])
        if isinstance(tracks, dict):
            return [Track(tracks, self._http)]

        return [Track(track, self._http) for track in tracks]

    async def add_tags(self, api_sig: str, sk: str, *tags: str) -> None:
        if len(tags) > 10:
            raise ValueError('Cannot add more than 10 tags')

        if not self.artist:
            return

        await self._http.add_album_tags(api_sig, sk, self.artist, self.name, tags)

    async def remove_tag(self, api_sig: str, sk: str, tag: str) -> None:
        if not self.artist:
            return
    
        await self._http.remove_album_tag(api_sig, sk, self.artist, self.name, tag)

    async def get_tags(
        self, *, user: Optional[str] = None
    ) -> List[Tag]:
        if self.mbid:
            data = await self._http.get_album_tags(mbid=self.mbid, user=user)
        else:
            data = await self._http.get_album_tags(self.artist, self.name, user=user)

        tags = data['tags'].get('tag', [])
        return [Tag(tag, self._http) for tag in tags]

    async def get_top_tags(self) -> List[Tag]:
        if self.mbid:
            data = await self._http.get_album_top_tags(mbid=self.mbid)
        else:
            data = await self._http.get_album_top_tags(self.artist, self.name)

        tags = data['toptags'].get('tag', [])
        return [Tag(tag, self._http) for tag in tags]

