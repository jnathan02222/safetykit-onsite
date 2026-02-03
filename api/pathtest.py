from db import DB
import asyncio
from tqdm import tqdm


async def main():
    db = DB()
    # Make sure to create the indexes
    print(
        [
            [artist.name for artist in path]
            for path in await db.shortest_path(38252, 49071733)
        ]
    )
    # artists = []
    # async for artist in db.all_artists():
    #     artists.append(artist)

    # artists_without_path = []
    # for artist in tqdm(artists):
    #     # Check for a path within 3 edges to The Beatles
    #     paths = await db.shortest_path(29812, artist.id)
    #     if len(paths) == 0:
    #         artists_without_path.append(artist.name)

    # print(artists_without_path)
    # print(len(artists_without_path))


asyncio.run(main())
