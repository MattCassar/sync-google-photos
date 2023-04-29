import sys

sys.path.append("..")

from gpsync.google_photos.client import GooglePhotosClient
from gpsync.google_photos.creds import load_credentials
from gpsync.google_photos.schemas.media_items import SearchMediaItemsRequest, SearchMediaItemsResponse


credentials = load_credentials("/Users/matt/personal/google-photos/credentials.json")
client = GooglePhotosClient.from_credentials(credentials)
albums = client.list_all_albums()
album = albums[0]

response = client.search_all_album_media_items(album)
print(response)
