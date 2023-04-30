from typing import List, Optional

from gpsync.google_photos.schemas.common import GoogleApiBaseModel


class SharedAlbumOptions(GoogleApiBaseModel):
    """SharedAlbumOptions type defined by Google.

    See: https://developers.google.com/photos/library/reference/rest/v1/albums#Album.SharedAlbumOptions"""

    is_collaborative: bool
    is_commentable: bool


class ShareInfo(GoogleApiBaseModel):
    """ShareInfo type defined by Google.

    See: https://developers.google.com/photos/library/reference/rest/v1/albums#Album.ShareInfo"""

    shared_album_options: SharedAlbumOptions
    shareable_url: str
    share_token: str
    is_joined: bool
    is_owned: bool
    is_joinable: bool


class Album(GoogleApiBaseModel):
    """Album type defined by Google.

    See: https://developers.google.com/photos/library/reference/rest/v1/albums#Album"""

    id: str
    title: Optional[str]
    product_url: Optional[str]
    media_items_count: Optional[str] = None
    cover_photo_base_url: Optional[str] = None
    cover_photo_media_item_id: Optional[str] = None
    is_writeable: Optional[bool] = None
    share_info: Optional[ShareInfo] = None


class ListAlbumsRequest(GoogleApiBaseModel):
    # Maximum number of albums to return in the response.
    # Fewer albums might be returned than the specified number.
    # The default pageSize is 20, the maximum is 50.
    page_size: int = 50

    page_token: Optional[None] = None

    # If set, the results exclude media items that were not created by this app.
    # Defaults to false (all albums are returned). This field is ignored if the
    # photoslibrary.readonly.appcreateddata scope is used.
    exclude_non_app_created_data: bool = False


class ListAlbumsResponse(GoogleApiBaseModel):
    albums: List[Album]
    next_page_token: Optional[str] = None


class ListSharedAlbumsRequest(GoogleApiBaseModel):
    # Maximum number of albums to return in the response.
    # Fewer albums might be returned than the specified number.
    # The default pageSize is 20, the maximum is 50.
    page_size: int = 50

    page_token: Optional[None] = None

    # If set, the results exclude media items that were not created by this app.
    # Defaults to false (all albums are returned). This field is ignored if the
    # photoslibrary.readonly.appcreateddata scope is used.
    exclude_non_app_created_data: bool = False


class ListSharedAlbumsResponse(GoogleApiBaseModel):
    shared_albums: List[Album]
    next_page_token: Optional[str] = None
