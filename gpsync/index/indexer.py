from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.future import Engine

from gpsync.google_photos.client import GooglePhotosClient
from gpsync.models.index import Album as AlbumIndex
from gpsync.models.index import Content as ContentIndex
from gpsync.models.index import Download as DownloadIndex


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
                
                session.add(AlbumIndex(
                    id=album.id,
                    title=album.title
                ))

            session.commit()
