from typing import Any, Dict, List, Optional, Sequence

import aiohttp
import asyncio

from .errors import HTTPException

class HTTPClient:
    URL = 'http://ws.audioscrobbler.com/2.0/'

    def __init__(self, api_key: str, session: Optional[aiohttp.ClientSession]):
        self.api_key = api_key
        self.session = session

    async def _create_session(self) -> aiohttp.ClientSession:
        if not self.session:
            self.session = aiohttp.ClientSession()

        return self.session

    async def close(self) -> None:
        if not self.session:
            return

        await self.session.close()

    async def read(self, url: str) -> bytes:
        session = await self._create_session()
        async with session.get(url) as response:
            return await response.read()

    async def request(self, method: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        session = await self._create_session()

        params = params or {}
        
        params.update({'method': method, 'api_key': self.api_key, 'format': 'json', **kwargs})
        params = {k: v for k, v in params.items() if v is not None}

        for key, value in params.items():
            if isinstance(value, bool):
                params[key] = 1 if value else 0

        async with session.get(self.URL, params=params) as response:
            if response.status == 429:
                retry_after = float(response.headers['Retry-After'])
                await asyncio.sleep(retry_after)

                return await self.request(method, **kwargs)

            data = await response.json()
            if response.status != 200 or 'error' in data:
                raise HTTPException(data)

            return data

    async def add_album_tags(self, api_sig: str, sk: str, artist: str, album: str, tags: Sequence[str]) -> None:
        await self.request('album.addTags', api_sig=api_sig, sk=sk, artist=artist, album=album, tags=','.join(tags))

    async def remove_album_tag(self, api_sig: str, sk: str, artist: str, album: str, tag: str) -> None:
        await self.request('album.removeTag', api_sig=api_sig, sk=sk, artist=artist, album=album, tag=tag)

    async def get_album_info(
        self, 
        artist: Optional[str] = None, 
        album: Optional[str] = None,
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        username: Optional[str] = None, 
        lang: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.request(
            'album.getInfo', 
            artist=artist, 
            album=album, 
            mbid=mbid, 
            autocorrect=autocorrect, 
            username=username, 
            lang=lang
        )
    
    async def get_album_tags(
        self, 
        artist: Optional[str] = None, 
        album: Optional[str] = None,
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.request(
            'album.getTags', 
            artist=artist, 
            album=album, 
            mbid=mbid, 
            autocorrect=autocorrect, 
            user=user
        )

    async def get_album_top_tags(
        self, 
        artist: Optional[str] = None, 
        album: Optional[str] = None,
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None
    ) -> Dict[str, Any]:
        return await self.request(
            'album.getTopTags', 
            artist=artist, 
            album=album, 
            mbid=mbid, 
            autocorrect=autocorrect
        )

    async def search_albums(self, album: str, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('album.search', album=album, limit=limit, page=page)

    async def add_artist_tags(self, api_sig: str, sk: str, artist: str, tags: Sequence[str]) -> None:
        await self.request('artist.addTags', api_sig=api_sig, sk=sk, artist=artist, tags=','.join(tags))

    async def remove_artist_tag(self, api_sig: str, sk: str, artist: str, tag: str) -> None:
        await self.request('artist.removeTag', api_sig=api_sig, sk=sk, artist=artist, tag=tag)

    async def get_artist_correction(self, artist: str) -> Dict[str, Any]:
        return await self.request('artist.getCorrection', artist=artist)

    async def get_artist_info(
        self, 
        artist: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        username: Optional[str] = None,
        lang: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.request('artist.getInfo', artist=artist, mbid=mbid, autocorrect=autocorrect, username=username, lang=lang)

    async def get_artist_similar(
        self, 
        artist: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('artist.getSimilar', artist=artist, mbid=mbid, autocorrect=autocorrect, limit=limit)

    async def get_artist_tags(
        self, 
        artist: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.request('artist.getTags', artist=artist, mbid=mbid, autocorrect=autocorrect, user=user)

    async def get_artist_top_albums(
        self, 
        artist: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('artist.getTopAlbums', artist=artist, mbid=mbid, autocorrect=autocorrect, limit=limit, page=page)

    async def get_artist_top_tags(
        self, 
        artist: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None
    ) -> Dict[str, Any]:
        return await self.request('artist.getTopTags', artist=artist, mbid=mbid, autocorrect=autocorrect)

    async def get_artist_top_tracks(
        self, 
        artist: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('artist.getTopTracks', artist=artist, mbid=mbid, autocorrect=autocorrect, limit=limit, page=page)

    async def search_artists(self, artist: str, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('artist.search', artist=artist, limit=limit, page=page)

    async def get_chart_top_artists(self, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('chart.getTopArtists', limit=limit, page=page)

    async def get_chart_top_tags(self, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('chart.getTopTags', limit=limit, page=page)
    
    async def get_chart_top_tracks(self, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('chart.getTopTracks', limit=limit, page=page)

    async def get_geo_top_artists(
        self, 
        country: str, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('geo.getTopArtists', country=country, limit=limit, page=page)

    async def get_geo_top_tracks(
        self, 
        country: str, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('geo.getTopTracks', country=country, limit=limit, page=page)
    
    async def get_library_artists(
        self, 
        user: str, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('library.getArtists', user=user, limit=limit, page=page)

    async def get_tag_info(self, tag: str, lang: Optional[str] = None) -> Dict[str, Any]:
        return await self.request('tag.getInfo', tag=tag, lang=lang)

    async def get_tag_similar(self, tag: str) -> Dict[str, Any]:
        return await self.request('tag.getSimilar', tag=tag)

    async def get_tag_top_albums(self, tag: str, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('tag.getTopAlbums', tag=tag, limit=limit, page=page)
    
    async def get_tag_top_artists(self, tag: str, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('tag.getTopArtists', tag=tag, limit=limit, page=page)

    async def get_tag_top_tracks(self, tag: str, limit: Optional[int] = None, page: Optional[int] = None) -> Dict[str, Any]:
        return await self.request('tag.getTopTracks', tag=tag, limit=limit, page=page)

    async def get_tag_weekly_chart_list(self, tag: str) -> Dict[str, Any]:
        return await self.request('tag.getWeeklyChartList', tag=tag)

    async def add_track_tags(
        self, api_sig: str, sk: str, artist: str, track: str, tags: Sequence[str]
    ) -> Dict[str, Any]:
        return await self.request(
            'track.addTags', api_sig=api_sig, artist=artist, track=track, tags=','.join(tags), sk=sk
        )

    async def get_track_correction(self, artist: str, track: str) -> Dict[str, Any]:
        return await self.request('track.getCorrection', artist=artist, track=track)

    async def get_track_info(
        self, 
        artist: Optional[str] = None, 
        track: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.request('track.getInfo', artist=artist, track=track, mbid=mbid, autocorrect=autocorrect, username=username)

    async def get_track_tags(
        self, 
        artist: Optional[str] = None, 
        track: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None, 
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.request(
            'track.getTags', artist=artist, track=track, mbid=mbid, autocorrect=autocorrect, user=user
        )

    async def get_track_top_tags(
        self, 
        artist: Optional[str] = None, 
        track: Optional[str] = None, 
        mbid: Optional[str] = None, 
        autocorrect: Optional[bool] = None
    ) -> Dict[str, Any]:
        return await self.request('track.getTopTags', artist=artist, track=track, mbid=mbid, autocorrect=autocorrect)

    async def love_track(self, api_sig: str, sk: str, artist: str, track: str) -> Dict[str, Any]:
        return await self.request('track.love', api_sig=api_sig, artist=artist, track=track, sk=sk)

    # TODO: track.scrobble

    async def search_track(
        self, 
        track: str, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('track.search', track=track, limit=limit, page=page)

    async def unlove_track(self, api_sig: str, sk: str, artist: str, track: str) -> Dict[str, Any]:
        return await self.request('track.unlove', api_sig=api_sig, artist=artist, track=track, sk=sk)

    async def remove_track_tag(self, api_sig: str, sk: str, artist: str, track: str, tag: str) -> Dict[str, Any]:
        return await self.request('track.removeTag', api_sig=api_sig, artist=artist, track=track, tag=tag, sk=sk)

    async def get_user_info(self, user: str) -> Dict[str, Any]:
        return await self.request('user.getInfo', user=user)

    async def get_user_loved_tracks(
        self, 
        user: str, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getLovedTracks', user=user, limit=limit, page=page)

    async def get_user_friends(
        self, 
        user: str, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getFriends', user=user, limit=limit, page=page)

    async def get_user_personal_tags(
        self, 
        tag: str, 
        user: str,
        tagging_type: str,
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getPersonalTags', tag=tag, user=user, taggingtype=tagging_type, limit=limit, page=page)

    async def get_user_recent_tracks(
        self, 
        user: str, 
        limit: Optional[int] = None, 
        page: Optional[int] = None,
        from_: Optional[int] = None,
        to: Optional[int] = None,
        extended: Optional[bool] = None
    ) -> Dict[str, Any]:
        return await self.request(
            'user.getRecentTracks', {'from': from_}, user=user, limit=limit, page=page, to=to, extended=extended
        )

    async def get_user_top_albums(
        self, 
        user: str, 
        period: Optional[str] = None, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getTopAlbums', user=user, period=period, limit=limit, page=page)

    async def get_user_top_artists(
        self, 
        user: str, 
        period: Optional[str] = None, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getTopArtists', user=user, period=period, limit=limit, page=page)
    
    async def get_user_top_tags(
        self, 
        user: str, 
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getTopTags', user=user, limit=limit)

    async def get_user_top_tracks(
        self, 
        user: str, 
        period: Optional[str] = None, 
        limit: Optional[int] = None, 
        page: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getTopTracks', user=user, period=period, limit=limit, page=page)
    
    async def get_user_weekly_album_chart(
        self, 
        user: str, 
        from_: Optional[int] = None,
        to: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getWeeklyAlbumChart', {'from': from_}, user=user, to=to)

    async def get_user_weekly_artist_chart(
        self, 
        user: str, 
        from_: Optional[int] = None,
        to: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getWeeklyArtistChart', {'from': from_}, user=user, to=to)

    async def get_user_weekly_chart_list(self, user: str) -> Dict[str, Any]:
        return await self.request('user.getWeeklyChartList', user=user)

    async def get_user_weekly_track_chart(
        self, 
        user: str, 
        from_: Optional[int] = None,
        to: Optional[int] = None
    ) -> Dict[str, Any]:
        return await self.request('user.getWeeklyTrackChart', {'from': from_}, user=user, to=to)