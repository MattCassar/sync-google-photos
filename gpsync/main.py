import sys

sys.path.append("..")

from gpsync.google_photos.client import GooglePhotosClient
from gpsync.google_photos.creds import load_credentials

credentials = load_credentials("/Users/matt/personal/google-photos/credentials.json")
client = GooglePhotosClient.from_credentials(credentials)
albums = client.list_all_albums()
album = albums[1]
print(album.title)

google_photos = client.download_album(album)
print(google_photos)
