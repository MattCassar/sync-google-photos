import sys

sys.path.append("..")

from gpsync.google_photos.client import GooglePhotosClient
from gpsync.google_photos.creds import fetch_or_load_credentials
from gpsync.index.indexer import GooglePhotosIndexer

ALBUM_ID = ""
BASE_PATH = ""
credentials = fetch_or_load_credentials(
    "/Users/matt/personal/google-photos/credentials.json", cache_filepath="creds.pickle"
)
client = GooglePhotosClient.from_credentials(credentials)
indexer = GooglePhotosIndexer(client=client)
indexer.index_albums()
indexer.index_album_content(ALBUM_ID)
indexer.download_indexed_content(BASE_PATH)
