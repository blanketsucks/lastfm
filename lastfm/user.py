from __future__ import annotations

from typing import Any, Dict, List, Optional

from enum import Enum
import datetime

from .http import HTTPClient
from .image import Image
from .album import Album
from .artist import Artist
from .track import Track
from .tag import Tag

__all__ = ('Period', 'User')

class Period(str, Enum):
    Overall = 'overall'
    SevenDays = '7day'
    OneMonth = '1month'
    ThreeMonths = '3month'
    SixMonths = '6month'
    OneYear = '12month'

class User:
    __slots__ = (
        '_http',
        '_data',
        'name',
        'realname',
        'url',
        'country',
        'gender',
        'age',
        'playcount',
        'artist_count',
        'album_count',
        'track_count',
        'bootstrap',
        'subscriber'
    )

    def __init__(self, data: Dict[str, Any], http: HTTPClient) -> None:
        self._http = http
        self._data = data

        self.name: str = data['name']
        self.realname: str = data['realname']
        self.url: str = data['url']
        self.country: str = data['country']
        self.gender: str = data['gender']
        self.age: int = int(data['age'])
        self.playcount: int = int(data['playcount'])
        self.artist_count: int = int(data['playcount'])
        self.album_count: int = int(data['playcount'])
        self.track_count: int = int(data['playcount'])
        self.bootstrap: int = int(data['playcount'])
        self.subscriber: int = int(data['playcount'])

    def __repr__(self) -> str:
        return f'<User name={self.name!r}>'

    @property
    def images(self) -> List[Image]:
        return [Image(image, self._http) for image in self._data['image']]

    async def get_top_artists(self, period: Period = Period.Overall) -> List[Artist]:
        data = await self._http.get_user_top_artists(self.name, period)
        return [Artist(artist, self._http) for artist in data['topartists']['artist']]

    async def get_top_albums(self, period: Period = Period.Overall) -> List[Album]:
        data = await self._http.get_user_top_albums(self.name, period)
        return [Album(album, self._http) for album in data['topalbums']['album']]

    async def get_top_tracks(self, period: Period = Period.Overall) -> List[Track]:
        data = await self._http.get_user_top_tracks(self.name, period)
        return [Track(track, self._http) for track in data['toptracks']['track']]

    async def get_top_tags(self) -> List[Tag]:
        data = await self._http.get_user_top_tags(self.name)
        return [Tag(tag, self._http) for tag in data['toptags']['tag']]

    async def get_recent_tracks(
        self,
        *,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        from_: Optional[datetime.datetime] = None,
        to: Optional[datetime.datetime] = None,
        extended: Optional[bool] = None
    ) -> List[Track]:
        kwargs: Dict[str, Any] = {
            'limit': limit,
            'page': page,
            'extended': extended
        }

        if from_ is not None:
            kwargs['from'] = int(from_.timestamp())
        if to is not None:
            kwargs['to'] = int(to.timestamp())

        data = await self._http.get_user_recent_tracks(self.name, **kwargs)
        return [Track(track, self._http) for track in data['recenttracks']['track']]

    async def get_weekly_artist_chart(self) -> List[Artist]:
        data = await self._http.get_user_weekly_artist_chart(self.name)
        return [Artist(artist, self._http) for artist in data['weeklyartistchart']['artist']]

    async def get_weekly_album_chart(self) -> List[Album]:
        data = await self._http.get_user_weekly_album_chart(self.name)
        return [Album(album, self._http) for album in data['weeklyalbumchart']['album']]

    async def get_weekly_track_chart(self) -> List[Track]:
        data = await self._http.get_user_weekly_track_chart(self.name)
        return [Track(track, self._http) for track in data['weeklytrackchart']['track']]

    async def get_loved_tracks(self) -> List[Track]:
        data = await self._http.get_user_loved_tracks(self.name)
        return [Track(track, self._http) for track in data['lovedtracks']['track']]
    
    async def get_friends(self) -> List[User]:
        data = await self._http.get_user_friends(self.name)
        return [User(user, self._http) for user in data['friends']['user']]
