from typing import List

from pydantic import BaseModel
from sqlalchemy.future import Engine
from sqlmodel import Session, SQLModel, create_engine, select
from tqdm import tqdm

from gpsync.google_photos.client import GooglePhotosClient
from gpsync.models.index import Album as AlbumIndex
from gpsync.models.index import Content as ContentIndex
from gpsync.models.index import Download as DownloadIndex
from gpsync.utils import create_directories


def get_engine(url: str = "sqlite:///sqlite.db") -> Engine:
    engine = create_engine(url)
    SQLModel.metadata.create_all(engine)
    return engine


class GooglePhotosIndexer(BaseModel):
    client: GooglePhotosClient

    def index_albums(self):
        albums = self.client.list_all_albums(include_shared=True)
        with Session(get_engine()) as session:
            for album in albums:
                indexed_album = session.get(AlbumIndex, album.id)

                if indexed_album is not None:
                    continue

                session.add(AlbumIndex(id=album.id, title=album.title))

            session.commit()

    def index_album_content(self, album_id: str):
        with Session(get_engine()) as session:
            album = session.get(AlbumIndex, album_id)
            if album is None:
                return

            google_photos_album = album.to_google_photos_api_album()
            media_items = self.client.search_non_archived_album_media_items(
                google_photos_album
            )
            for media_item in tqdm(
                media_items,
                unit=" media items",
                desc=f"Indexing {album.title} media items",
                total=len(media_items),
            ):
                indexed_content = session.get(ContentIndex, media_item.id)

                if indexed_content is not None:
                    continue

                content = ContentIndex.from_media_item(media_item)
                content.album_id = album_id

                session.add(content)

            session.commit()

    def download_indexed_content(self, base_path: str):
        with Session(get_engine()) as session:
            content: List[ContentIndex] = list(session.exec(select(ContentIndex)))

            media_items = [item.to_media_item() for item in content]
            google_photos_content = self.client.download_media_items(
                media_items,
                "Downloading indexed media items",
            )

            for item in google_photos_content:
                content_id = item.media_item.id

                album_title = session.exec(select(AlbumIndex.title).where(AlbumIndex.id == ContentIndex.album_id).where(ContentIndex.id == content_id)).first()
                album_title = album_title or "No Album"

                local_filename = item.media_item.filename
                local_filepath = f"{base_path}/{album_title}/{local_filename}"

                create_directories(local_filepath)

                DownloadIndex(
                    local_filepath=local_filepath,
                    local_filename=local_filename,
                    content_id=content_id,
                )
                item.save(local_filepath)

            session.commit()
