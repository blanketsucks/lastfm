# lastfm

## Example Usage

```py
import lastfm
import asyncio

API_KEY = 'YOUR_API_KEY'

async def main():
    async with lastfm.Client(API_KEY) as client:
        track = await client.get_track_info('TUYU', 'I hope you can be an adult someday')
        print(track.name)

asyncio.run(main())
```

Fetching a user's recent tracks:

```py
import lastfm
import asyncio

API_KEY = 'YOUR_API_KEY'

async def main():
    async with lastfm.Client(API_KEY) as client:
        user = await client.get_user_info('blanketsucks')
        tracks = await user.get_recent_tracks()

        for track in tracks:
            print(track.name)

        # Or, if you want to use the pagination method:
        async for track in lastfm.Paginator(user.get_recent_tracks):
            # Adding a `max` argument to the pagintor constructor will limit the number of elements returned
            # and the `limit` argument is the amount of elements to fetch per request.
            # Any extra arguments are passed to the function.

            print(track.name)


asyncio.run(main())
```

## Installation

Installation is done with git (Python 3.8 or higher is required):

```console
$ pip install git+https://github.com/blanketsucks/lastfm.git
```

## Documentation

No.
