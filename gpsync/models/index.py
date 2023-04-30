import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Album(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: Optional[str] = None


class Content(SQLModel, table=True):
    id: str = Field(primary_key=True)
    album_id: Optional[str] = Field(default=None, foreign_key="album.id")
    base_url: str
    download_url: str
    google_photos_filename: str
    content_creation_time: datetime.datetime
    height: int
    width: int
    mime_type: str
    description: Optional[str] = None
    fps: Optional[float] = None
    created_at: datetime.datetime = Field(
        default=datetime.datetime.utcnow(), nullable=False
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, nullable=False
    )


class Download(SQLModel, table=True):
    local_filepath: str = Field(primary_key=True)
    local_filename: str
    content_id: str = Field(foreign_key="content.id")
    timestamp: datetime.datetime = Field(
        default=datetime.datetime.utcnow(), nullable=False
    )
