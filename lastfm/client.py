from typing import Any, Optional, List

import aiohttp

from .http import HTTPClient
from .album import Album
from .artist import Artist
from .track import Track
from .user import User
from .tag import Tag

__all__ = 'Client',

class Client:
    def __init__(self, api_key: str, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.api_key = api_key
        self.http = HTTPClient(api_key, session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args: Any):
        await self.close()

    async def close(self) -> None:
        await self.http.close()

    async def get_album_info(
        self, 
        artist: Optional[str] = None, 
        album: Optional[str] = None, 
        *, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        username: Optional[str] = None,
        lang: Optional[str] = None
    ) -> Album:
        if artist is None and album is None:
            if mbid is None:
                raise ValueError('Either artist and album or mbid must be provided')
        else:
            if mbid is not None:
                raise ValueError('Cannot provide mbid with artist and album')

        data = await self.http.get_album_info(
            artist=artist,
            album=album,
            mbid=mbid,
            autocorrect=autocorrect,
            username=username,
            lang=lang
        )

        return Album(data['album'], self.http)

    async def get_artist_info(
        self, 
        artist: Optional[str] = None, 
        *, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        username: Optional[str] = None,
        lang: Optional[str] = None
    ) -> Artist:
        if artist is None:
            if mbid is None:
                raise ValueError('Either artist or mbid must be provided')
        else:
            if mbid is not None:
                raise ValueError('Cannot provide mbid with artist')

        data = await self.http.get_artist_info(
            artist=artist,
            mbid=mbid,
            autocorrect=autocorrect,
            username=username,
            lang=lang
        )

        return Artist(data['artist'], self.http)

    async def get_track_info(
        self, 
        artist: Optional[str] = None, 
        track: Optional[str] = None, 
        *, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        username: Optional[str] = None
    ) -> Track:
        if artist is None and track is None:
            if mbid is None:
                raise ValueError('Either artist and track or mbid must be provided')
        else:
            if mbid is not None:
                raise ValueError('Cannot provide mbid with artist and track')

        data = await self.http.get_track_info(
            artist=artist,
            track=track,
            mbid=mbid,
            autocorrect=autocorrect,
            username=username,
        )

        return Track(data['track'], self.http)

    async def get_user_info(self, user: str) -> User:
        data = await self.http.get_user_info(user)
        return User(data['user'], self.http)

    async def search_albums(
        self, 
        album: str, 
        *, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> List[Album]:
        data = await self.http.search_albums(album, limit=limit, page=page)
        return [Album(album, self.http) for album in data['results']['albummatches']['album']]

    async def search_artists(
        self, 
        artist: str, 
        *, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> List[Artist]:
        data = await self.http.search_artists(artist, limit=limit, page=page)
        return [Artist(artist, self.http) for artist in data['results']['artistmatches']['artist']]
    
    async def get_chart_top_tags(
        self, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Tag]:
        data = await self.http.get_chart_top_tags(limit, page)
        return [Tag(tag, self.http) for tag in data['tags']['tag']]
    
    async def get_country_top_tracks(
        self, country: str, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Track]:
        data = await self.http.get_geo_top_tracks(country, limit, page)
        return [Track(track, self.http) for track in data['tracks']['track']]
    
    async def get_country_top_artists(
        self, country: str, *, limit: Optional[int] = None, page: Optional[int] = None
    ) -> List[Artist]:
        data = await self.http.get_geo_top_artists(country, limit, page)
        return [Artist(artist, self.http) for artist in data['topartists']['artist']]