import os
import sys

sys.path.append("..")

from gpsync.google_photos.client import GooglePhotosClient
from gpsync.google_photos.creds import fetch_or_load_credentials
from gpsync.index.indexer import GooglePhotosIndexer


credentials = fetch_or_load_credentials(
    "/Users/matt/personal/google-photos/credentials.json", cache_filepath="creds.pickle"
)
client = GooglePhotosClient.from_credentials(credentials)
indexer = GooglePhotosIndexer(client=client)

def download_album(client):
    albums = client.list_all_albums()
    album = albums[1]
    print(album.title)

    google_photos_content = client.download_album(album)
    print(len(google_photos_content))
    print(google_photos_content[0].media_item)
    base_path = f"/Users/matt/personal/cheer-photos/{album.title}"
    os.makedirs(base_path, exist_ok=True)
    for photo_or_video in google_photos_content:
        photo_or_video.save(f"{base_path}/{photo_or_video.media_item.filename}")


# client.list_all_albums(include_shared=True)
indexer.index_albums()