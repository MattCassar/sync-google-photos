# from __future__ import annotations  # This is blocked by https://github.com/tiangolo/sqlmodel/issues/196
import datetime
import uuid
from typing import Any, List, Optional

from sqlmodel import Column, Enum, Field, Relationship, SQLModel

from gpsync.google_photos.schemas.albums import Album as GooglePhotosAlbum
from gpsync.google_photos.schemas.media_items import (
    MediaItem,
    MediaMetadata,
    Photo,
    Video,
    VideoProcessingStatus,
)


class AlbumDownloadRunLink(SQLModel, table=True):
    album_id: Optional[str] = Field(
        default=None, foreign_key="album.id", primary_key=True
    )
    download_run_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="download_run.id", primary_key=True
    )


class Album(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    title: Optional[str] = None
    download_runs: List["DownloadRun"] = Relationship(
        back_populates="albums", link_model=AlbumDownloadRunLink
    )

    def to_google_photos_api_album(self) -> "GooglePhotosAlbum":
        return GooglePhotosAlbum(id=self.id, title=self.title)


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
    status: Optional[VideoProcessingStatus] = Field(
        default=None,
        sa_column=Column(Enum(VideoProcessingStatus)),
    )
    created_at: datetime.datetime = Field(
        default=datetime.datetime.utcnow(),
        nullable=False,
    )
    updated_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        nullable=False,
    )

    @staticmethod
    def from_media_item(media_item: MediaItem) -> "Content":
        if media_item.media_metadata.photo is not None:
            download_url = f"{media_item.base_url}=d"
        elif media_item.media_metadata.video is not None:
            download_url = f"{media_item.base_url}=dv"
        else:
            raise ValueError(
                "media_item is neither a photo nor a video, this shouldn't happen."
            )

        content_creation_time = datetime.datetime.fromisoformat(
            media_item.media_metadata.creation_time.replace("Z", "+00:00")
        )

        fps = None
        status = None
        if media_item.media_metadata.video is not None:
            fps = media_item.media_metadata.video.fps
            status = media_item.media_metadata.video.status

        content = Content(
            id=media_item.id,
            base_url=media_item.base_url,
            download_url=download_url,
            google_photos_filename=media_item.filename,
            content_creation_time=content_creation_time,
            height=media_item.media_metadata.height,
            width=media_item.media_metadata.width,
            mime_type=media_item.mime_type,
            description=media_item.description,
            fps=fps,
            status=status,
        )
        return content

    def to_media_item(self) -> MediaItem:
        photo: Optional[Photo] = None
        video: Optional[Video] = None

        if "image" in self.mime_type:
            photo = Photo()
        elif "video" in self.mime_type:
            if self.fps is None or self.status is None:
                raise ValueError("fps and status cannot be None for videos")

            video = Video(fps=self.fps, status=self.status)
        else:
            raise ValueError(
                "media_item is neither a photo nor a video, this shouldn't happen."
            )

        media_metadata = MediaMetadata(
            creation_time=self.content_creation_time.isoformat().replace("+00:00", "Z"),
            width=str(self.width),
            height=str(self.height),
            photo=photo,
            video=video,
        )
        return MediaItem(
            id=self.id,
            product_url="",
            base_url=self.base_url,
            mime_type=self.mime_type,
            filename=self.google_photos_filename,
            description=self.description,
            media_metadata=media_metadata,
        )


class Download(SQLModel, table=True):
    local_filepath: str = Field(primary_key=True)
    local_filename: str
    content_id: str = Field(foreign_key="content.id")
    timestamp: datetime.datetime = Field(
        default=datetime.datetime.utcnow(),
        nullable=False,
    )
    download_run_id: uuid.UUID = Field(foreign_key="download_run.id")


class DownloadRun(SQLModel, table=True):
    """Download run for an individual album or piece of content."""

    __tablename__ = "download_run"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    base_filepath: str
    albums: List[Album] = Relationship(
        back_populates="download_runs",
        link_model=AlbumDownloadRunLink,
    )
    start_date: Optional[datetime.date] = Field(
        default=None,
        nullable=True,
    )
    end_date: datetime.date = Field(
        default=datetime.datetime.utcnow().date(),
        nullable=False,
    )
