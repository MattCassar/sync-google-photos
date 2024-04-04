from enum import Enum
from typing import List, Optional

from pydantic import Field

from gpsync.google_photos.schemas.common import (
    GoogleApiBaseModel,
    GoogleApiDate,
    GoogleApiDateRange,
)


class ContentCategory(str, Enum):
    NONE = "NONE"
    RECEIPTS = "RECEIPTS"  # Media items containing receipts.
    CITYSCAPES = "CITYSCAPES"  # Media items containing cityscapes.
    LANDSCAPES = "LANDSCAPES"  # Media items containing landscapes.
    SELFIES = "SELFIES"  # Media items that are selfies.
    PEOPLE = "PEOPLE"  # Media items containing people.
    PETS = "PETS"  # Media items containing pets.
    WEDDINGS = "WEDDINGS"  # Media items from weddings.
    BIRTHDAYS = "BIRTHDAYS"  # Media items from birthdays.
    DOCUMENTS = "DOCUMENTS"  # Media items containing documents.
    TRAVEL = "TRAVEL"  # Media items taken during travel.
    ANIMALS = "ANIMALS"  # Media items containing animals.
    FOOD = "FOOD"  # Media items containing food.
    SPORT = "SPORT"  # Media items from sporting events.
    NIGHT = "NIGHT"  # Media items taken at night.
    PERFORMANCES = "PERFORMANCES"  # Media items from performances.
    WHITEBOARDS = "WHITEBOARDS"  # Media items containing whiteboards.
    SCREENSHOTS = "SCREENSHOTS"  # Media items that are screenshots.
    UTILITY = "UTILTY"  # Media items that are considered to be utility. These include, but aren't limited to documents, screenshots, whiteboards etc.
    ARTS = "ART"  # Media items containing art.
    CRAFTS = "CRAFTS"  # Media items containing crafts.
    FASHION = "FASHION"  # Media items related to fashion.
    HOUSES = "HOUSES"  # Media items containing houses.
    GARDENS = "GARDENS"  # Media items containing gardens.
    FLOWERS = "FLOWERS"  # Media items containing flowers.
    HOLIDAYS = "HOLIDAYS"  # Media items containing holidays.


class MediaType(str, Enum):
    ALL_MEDIA = "ALL_MEDIA"
    VIDEO = "VIDEO"
    PHOTO = "PHOTO"


class Feature(str, Enum):
    NONE = "NONE"
    FAVORITES = "FAVORITES"


class DateFilter(GoogleApiBaseModel):
    dates: Optional[List[GoogleApiDate]]
    ranges: Optional[List[GoogleApiDateRange]]


class ContentFilter(GoogleApiBaseModel):
    include_content_filter_categories: Optional[List[ContentCategory]]
    exclude_content_filter_categories: Optional[List[ContentCategory]]


class MediaTypeFilter(GoogleApiBaseModel):
    media_types: Optional[List[MediaType]]


class FeatureFilter(GoogleApiBaseModel):
    included_features: Optional[List[Feature]]


class Filters(GoogleApiBaseModel):
    date_filter: Optional[DateFilter] = None
    content_filter: Optional[ContentFilter] = None
    media_type_filter: Optional[MediaTypeFilter] = None
    feature_filter: Optional[FeatureFilter] = None
    include_archived_media: bool = False
    exclude_non_app_created_data: bool = False


class Photo(GoogleApiBaseModel):
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    focal_length: Optional[float] = None
    aperture_f_number: Optional[float] = None
    iso_equivalent: Optional[int] = None
    exposure_time: Optional[str] = None


class VideoProcessingStatus(Enum):
    # Video processing status is unknown.
    UNSPECIFIED = "UNSPECIFIED"

    # Video is being processed. The user sees an icon for this video in the Google Photos app;
    # however, it isn't playable yet.
    PROCESSING = "PROCESSING"

    # Video processing is complete and it is now ready for viewing.
    # Important: attempting to download a video not in the READY state may fail.
    READY = "READY"

    # Something has gone wrong and the video has failed to process.
    FAILED = "FAILED"


class Video(GoogleApiBaseModel):
    fps: float
    status: VideoProcessingStatus
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    iso_equivalent: Optional[int] = None
    exposure_time: Optional[str] = None


class ContributorInfo(GoogleApiBaseModel):
    profile_picture_base_url: str
    display_name: str


class MediaMetadata(GoogleApiBaseModel):
    creation_time: str
    width: str
    height: str
    photo: Optional[Photo] = None
    video: Optional[Video] = None


class MediaItem(GoogleApiBaseModel):
    id: str
    product_url: str
    base_url: str
    mime_type: str
    media_metadata: MediaMetadata
    filename: str
    description: Optional[str] = None
    contributor_info: Optional[ContributorInfo] = None

    @property
    def download_url(self) -> str:
        if self.media_metadata.photo is not None:
            return self.base_url + "=d"
        elif self.media_metadata.video is not None:
            return self.base_url + "=dv"
        else:
            raise ValueError(
                "media_item is neither a photo nor a video, this shouldn't happen."
            )


class GetMediaItemRequest(GoogleApiBaseModel):
    media_item_id: str


class SearchMediaItemsRequest(GoogleApiBaseModel):
    page_size: int = 100
    album_id: Optional[str] = None
    filters: Optional[Filters] = None
    order_by: Optional[str] = None
    page_token: Optional[str] = None


class SearchMediaItemsResponse(GoogleApiBaseModel):
    media_items: List[MediaItem] = Field(default_factory=list)
    next_page_token: Optional[str] = None
