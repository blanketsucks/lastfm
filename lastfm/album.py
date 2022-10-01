from typing import Dict, Any, List, Optional

from .http import HTTPClient

from .tag import Tag
from .image import Image
from .track import Track
from .wiki import Wiki

__all__ = 'Album',

class Album:
    __slots__ = ('_http', '_data', 'name', 'artist', 'mbid', 'url', 'listeners', 'playcount')

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        # This api is so dogshit there are 3 possible keys where the album name can be
        if 'name' in data:
            self.name: str = data['name']
        elif 'title' in data:
            self.name: str = data['title']
        elif '#text' in data:
            self.name: str = data['#text']

        self.artist: Optional[str] = data.get('artist')
        # From what i tested, the mbid is not present if the request was made using an mbid
        self.mbid: Optional[str] = data.get('mbid')
        self.url: Optional[str] = data.get('url')

        self.listeners: int = int(data.get('listeners', 0))
        self.playcount: int = int(data.get('playcount', 0))

    def __repr__(self) -> str:
        return f'<Album name={self.name!r}>'

    @property
    def wiki(self) -> Wiki:
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

        return [Tag(tag, self._http) for tag in data['tags']['tag']]

    async def get_top_tags(self) -> List[Tag]:
        if self.mbid:
            data = await self._http.get_album_top_tags(mbid=self.mbid)
        else:
            data = await self._http.get_album_top_tags(self.artist, self.name)

        return [Tag(tag, self._http) for tag in data['toptags']['tag']]

