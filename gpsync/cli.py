from typing import List, Optional

import typer

from gpsync.google_photos.client import GooglePhotosClient
from gpsync.google_photos.creds import fetch_or_load_credentials
from gpsync.index.indexer import GooglePhotosIndexer

app = typer.Typer()


@app.command()
def download(
    creds_path: str, download_path: str, album_titles: Optional[List[str]] = None
):
    credentials = fetch_or_load_credentials(creds_path, cache_filepath="creds.pickle")
    client = GooglePhotosClient.from_credentials(credentials)
    indexer = GooglePhotosIndexer(client=client)
    indexer.index_albums(album_titles=album_titles)
    indexer.index_all_album_content()
    indexer.download_indexed_content(download_path)
