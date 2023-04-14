from __future__ import annotations

from typing import Any, Dict, List, Optional

from enum import Enum
import datetime

from .http import HTTPClient
from .image import Image
from .album import Album
from .artist import Artist
from .track import Track, UserTrack, to_bool
from .tag import Tag
from .chart import WeeklyChart

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
        self.artist_count: int = int(data['artist_count'])
        self.album_count: int = int(data['album_count'])
        self.track_count: int = int(data['track_count'])
        self.bootstrap: bool = to_bool(data['bootstrap'])
        self.subscriber: bool = to_bool(data['subscriber'])

    def __repr__(self) -> str:
        return f'<User name={self.name!r}>'

    @property
    def images(self) -> List[Image]:
        return [Image(image, self._http) for image in self._data['image'] if image['#text']]

    @property
    def registered(self) -> datetime.datetime:
        data = self._data['registered']
        return datetime.datetime.fromtimestamp(int(data['unixtime']))

    async def get_top_artists(
        self, period: Period = Period.Overall, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Artist]:
        data = await self._http.get_user_top_artists(self.name, period, limit, page)
        return [Artist(artist, self._http) for artist in data['topartists']['artist']]

    async def get_top_albums(
        self, period: Period = Period.Overall, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Album]:
        data = await self._http.get_user_top_albums(self.name, period, limit, page)
        return [Album(album, self._http) for album in data['topalbums']['album']]

    async def get_top_tracks(
        self, period: Period = Period.Overall, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Track]:
        data = await self._http.get_user_top_tracks(self.name, period, limit, page)
        return [Track(track, self._http) for track in data['toptracks']['track']]

    async def get_top_tags(self, *, limit: Optional[int] = None) -> List[Tag]:
        data = await self._http.get_user_top_tags(self.name, limit)
        return [Tag(tag, self._http) for tag in data['toptags']['tag']]

    async def get_recent_tracks(
        self,
        *,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        extended: Optional[bool] = None
    ) -> List[UserTrack]:
        kwargs: Dict[str, Any] = {
            'limit': limit,
            'page': page,
            'extended': extended
        }

        if start is not None:
            kwargs['from_'] = int(start.timestamp())
        if end is not None:
            kwargs['to'] = int(end.timestamp())

        data = await self._http.get_user_recent_tracks(self.name, **kwargs)
        return [UserTrack(track, self._http) for track in data['recenttracks']['track']]

    async def get_weekly_artist_chart(
        self, *, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None
    ) -> List[Artist]:
        kwargs: Dict[str, Any] = {}
        if start is not None:
            kwargs['from_'] = int(start.timestamp())
        if end is not None:
            kwargs['to'] = int(end.timestamp())

        data = await self._http.get_user_weekly_artist_chart(self.name, **kwargs)
        return [Artist(artist, self._http) for artist in data['weeklyartistchart']['artist']]

    async def get_weekly_album_chart(
        self, *, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None
    ) -> List[Album]:
        kwargs: Dict[str, Any] = {}
        if start is not None:
            kwargs['from_'] = int(start.timestamp())
        if end is not None:
            kwargs['to'] = int(end.timestamp())

        data = await self._http.get_user_weekly_album_chart(self.name, **kwargs)
        return [Album(album, self._http) for album in data['weeklyalbumchart']['album']]

    async def get_weekly_track_chart(
        self, *, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None
    ) -> List[Track]:
        kwargs: Dict[str, Any] = {}
        if start is not None:
            kwargs['from_'] = int(start.timestamp())
        if end is not None:
            kwargs['to'] = int(end.timestamp())

        data = await self._http.get_user_weekly_track_chart(self.name, **kwargs)
        return [Track(track, self._http) for track in data['weeklytrackchart']['track']]
    
    async def get_weekly_chart_list(self) -> List[WeeklyChart]:
        data = await self._http.get_user_weekly_chart_list(self.name)
        return [WeeklyChart.from_dict(chart) for chart in data['weeklychartlist']['chart']]

    async def get_loved_tracks(
        self, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[UserTrack]:
        data = await self._http.get_user_loved_tracks(self.name, limit, page)
        tracks: List[UserTrack] = []

        for track in data['lovedtracks']['track']:
            track['loved'] = '1' # A bit of a hack since the API does not provide this field
            tracks.append(UserTrack(track, self._http))

        return tracks
    
    async def get_library_artists(
        self, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Artist]:
        data = await self._http.get_library_artists(self.name, limit, page)
        return [Artist(artist, self._http) for artist in data['artists']['artist']]
    
    async def get_friends(
        self, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[User]:
        data = await self._http.get_user_friends(self.name, limit, page)
        return [User(user, self._http) for user in data['friends']['user']]
