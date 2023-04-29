from pydantic import BaseModel

import piexif  # type: ignore
import piexif.helper  # type: ignore
from PIL import Image


from gpsync.google_photos.schemas.media_items import MediaItem


class GooglePhoto(BaseModel):
    media_item: MediaItem
    image: Image.Image

    class Config:
        arbitrary_types_allowed = True

    def save(self, path: str) -> None:
        exif_dict = piexif.load(self.image.info["exif"])
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(
            self.media_item.description, encoding="unicode"
        )

        # This is a known bug with piexif (https://github.com/hMatoba/Piexif/issues/95)
        if 41729 in exif_dict["Exif"]:
            exif_dict["Exif"][41729] = bytes(exif_dict["Exif"][41729])

        exif_bytes = piexif.dump(exif_dict)
        self.image.save(path, exif=exif_bytes)


class GoogleVideo(BaseModel):
    media_item: MediaItem
    video: bytes

    class Config:
        arbitrary_types_allowed = True

    def save(self, path: str) -> None:
        with open(path, "wb") as file:
            file.write(self.video)
