from abc import ABC, abstractmethod

import piexif  # type: ignore
import piexif.helper  # type: ignore
from PIL import Image
from pydantic import BaseModel

from gpsync.google_photos.schemas.media_items import MediaItem


class GooglePhotosContent(BaseModel, ABC):
    media_item: MediaItem

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def save(self, path: str) -> None:
        raise NotImplementedError()


class GooglePhoto(GooglePhotosContent):
    image: Image.Image

    class Config:
        arbitrary_types_allowed = True

    def save(self, path: str) -> None:
        try:
            exif_dict = piexif.load(self.image.info["exif"])
            exif_dict["Exif"][
                piexif.ExifIFD.UserComment
            ] = piexif.helper.UserComment.dump(
                self.media_item.description or "", encoding="unicode"
            )

            # This is a known bug with piexif (https://github.com/hMatoba/Piexif/issues/95)
            if 41729 in exif_dict["Exif"]:
                exif_dict["Exif"][41729] = bytes(exif_dict["Exif"][41729])

            exif_bytes = piexif.dump(exif_dict)
        except KeyError:
            exif_bytes = None

        self.image.save(path, exif=exif_bytes)


class GoogleVideo(GooglePhotosContent):
    video: bytes

    class Config:
        arbitrary_types_allowed = True

    def save(self, path: str) -> None:
        with open(path, "wb") as file:
            file.write(self.video)
