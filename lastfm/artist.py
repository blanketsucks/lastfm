from __future__ import annotations

from typing import Dict, Any, Optional, List, TYPE_CHECKING

from .http import HTTPClient

from .tag import Tag
from .image import Image
from .wiki import Wiki

if TYPE_CHECKING:
    from .album import Album

__all__ = ('Artist', 'ArtistBio')

def to_bool(value: str) -> bool:
    return value == '1'

class ArtistBio(Wiki):
    __slots__ = Wiki.__slots__ + ('links',)

    def __init__(self, data: Dict[str, Any]) -> None:
        super().__init__(data)
        self.links: Dict[str, str] = data['links']

    def __repr__(self) -> str:
        return f'<ArtistBio published={self.published!r}>'

class Artist:
    __slots__ = (
        '_http',
        '_data',
        'name',
        'mbid',
        'url',
        'streamable',
        'ontour',
        'listeners',
        'playcount',
    )

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        if '#text' in data:
            self.name: str = data['#text']
        else:
            self.name: str = data['name']

        self.url: Optional[str] = data.get('url')
        self.mbid: Optional[str] = data.get('mbid')

        streamable = data.get('streamable')
        self.streamable = to_bool(streamable) if streamable else False

        ontour = data.get('ontour')
        self.ontour = to_bool(ontour) if ontour else False

        if 'stats' in data:
            self.listeners: int = int(data['stats']['listeners'])
            self.playcount: int = int(data['stats']['playcount'])
        else:
            self.listeners = 0
            self.playcount = 0
       
    def __repr__(self) -> str:
        return f'<Artist name={self.name!r}>'

    @property
    def images(self) -> List[Image]:
        return [Image(image, self._http) for image in self._data.get('image', [])]

    @property
    def tags(self) -> List[Tag]:
        tags = self._data.get('tags', {}).get('tag', [])
        return [Tag(tag, self._http) for tag in tags]
    
    @property
    def similar(self) -> List[Artist]:
        similar = self._data.get('similar', {}).get('artist', [])
        return [Artist(artist, self._http) for artist in similar]

    async def add_tags(self, api_sig: str, sk: str, *tags: str) -> None:
        if len(tags) > 10:
            raise ValueError('Cannot add more than 10 tags')

        await self._http.add_artist_tags(api_sig, sk, self.name, tags)

    async def remove_tag(self, api_sig: str, sk: str, tag: str) -> None:
        await self._http.remove_artist_tag(api_sig, sk, self.name, tag)

    async def get_tags(
        self, *, user: Optional[str] = None
    ) -> List[Tag]:
        data = await self._http.get_artist_tags(self.name, user=user)

        tags = data['tags'].get('tag', [])    
        return [Tag(tag, self._http) for tag in tags]

    async def get_top_tags(self) -> List[Tag]:
        data = await self._http.get_artist_top_tags(self.name)
        return [Tag(tag, self._http) for tag in data['toptags']['tag']]

    async def get_similar(self) -> List[Artist]:
        data = await self._http.get_artist_similar(self.name)
        return [Artist(artist, self._http) for artist in data['similarartists']['artist']]

    async def get_top_albums(self) -> List[Album]:
        from .album import Album

        data = await self._http.get_artist_top_albums(self.name)
        return [Album(album, self._http) for album in data['topalbums']['album']]