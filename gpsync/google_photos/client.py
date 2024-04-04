from __future__ import annotations

import io
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import requests
from google.oauth2.credentials import Credentials  # type: ignore
from googleapiclient.discovery import Resource, build  # type: ignore
from PIL import Image
from pydantic import BaseModel
from tqdm import tqdm

from gpsync.content.content_types import GooglePhoto, GooglePhotosContent, GoogleVideo
from gpsync.google_photos.schemas.albums import (
    Album,
    ListAlbumsRequest,
    ListAlbumsResponse,
    ListSharedAlbumsRequest,
    ListSharedAlbumsResponse,
)
from gpsync.google_photos.schemas.media_items import (
    GetMediaItemRequest,
    MediaItem,
    SearchMediaItemsRequest,
    SearchMediaItemsResponse,
)


class GooglePhotosClient(BaseModel):
    client: Resource

    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def from_credentials(credentials: Credentials) -> GooglePhotosClient:
        if not credentials.valid:
            raise ValueError("Must provide valid credentials")

        client = build(
            "photoslibrary",
            "v1",
            credentials=credentials,
            static_discovery=False,
        )

        return GooglePhotosClient(client=client)

    def list_albums(self, request: ListAlbumsRequest) -> ListAlbumsResponse:
        response = self.client.albums().list(**request.dict(by_alias=True)).execute()
        return ListAlbumsResponse(**response)

    def list_all_albums(self, include_shared: bool = False) -> List[Album]:
        request = ListAlbumsRequest()
        response = self.list_albums(request)
        albums = response.albums

        while response.next_page_token is not None:
            request = ListAlbumsRequest(page_token=response.next_page_token)
            response = self.list_albums(request)
            albums.extend(response.albums)

        if include_shared:
            shared_albums = self.list_all_shared_albums()
            albums.extend(shared_albums)

        return albums

    def list_shared_albums(
        self, request: ListSharedAlbumsRequest
    ) -> ListSharedAlbumsResponse:
        response = (
            self.client.sharedAlbums().list(**request.dict(by_alias=True)).execute()
        )
        return ListSharedAlbumsResponse(**response)

    def list_all_shared_albums(self) -> List[Album]:
        request = ListSharedAlbumsRequest()
        response = self.list_shared_albums(request)
        shared_albums = response.shared_albums

        while response.next_page_token is not None:
            request = ListSharedAlbumsRequest(page_token=response.next_page_token)
            response = self.list_shared_albums(request)
            shared_albums.extend(response.shared_albums)

        return shared_albums

    def get_media_item(self, media_item_id: str) -> MediaItem:
        request = GetMediaItemRequest(media_item_id=media_item_id)
        response = self.client.mediaItems().get(**request.dict(by_alias=True)).execute()
        return MediaItem(**response)

    def search_media_items(
        self, request_body: SearchMediaItemsRequest
    ) -> SearchMediaItemsResponse:
        response = (
            self.client.mediaItems()
            .search(body=request_body.dict(by_alias=True))
            .execute()
        )
        return SearchMediaItemsResponse(**response)

    def search_non_archived_album_media_items(self, album: Album) -> List[MediaItem]:
        """Search non-archived Google Photos album media.

        Google Photos does not currently allow archived media to be searched programmatically.
        If media in an album has been archived, it can still be searched by searching all media items, but
        this does not allow the content to be linked back to the album that it is shared under.
        There may be some hacks for this, but currently it is unknown whether it is possible
        to easily connect archived media back to the album."""
        request = SearchMediaItemsRequest(album_id=album.id, page_size=100)
        response = self.search_media_items(request)
        media_items = response.media_items

        while response.next_page_token is not None:
            request.page_token = response.next_page_token
            response = self.search_media_items(request)
            media_items.extend(response.media_items)

        return media_items

    def download_media_item(
        self, media_item: MediaItem
    ) -> Optional[GooglePhotosContent]:
        response = requests.get(media_item.download_url)
        is_download_url_stale = response.status_code == 403
        if is_download_url_stale:
            media_item_with_refreshed_download_url = self.get_media_item(media_item.id)
            response = requests.get(media_item_with_refreshed_download_url.download_url)

        if response.status_code >= 400:
            raise RuntimeError(f"Failed to download media_item {media_item.filename}")

        google_photos_content: Optional[GooglePhotosContent] = None
        if media_item.media_metadata.photo is not None:
            image = Image.open(io.BytesIO(response.content))
            google_photos_content = GooglePhoto(media_item=media_item, image=image)
        elif media_item.media_metadata.video is not None:
            google_photos_content = GoogleVideo(
                media_item=media_item, video=response.content
            )
        else:
            raise ValueError(
                "media_item is neither a photo nor a video, this shouldn't happen."
            )

        return google_photos_content

    def download_media_items(
        self, media_items: List[MediaItem], desc: str, num_threads: int = 8
    ) -> List[GooglePhotosContent]:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            google_photos_content: List[GooglePhotosContent] = list(
                tqdm(
                    executor.map(self.download_media_item, media_items),  # type: ignore
                    unit=" media items",
                    desc=desc,
                    total=len(media_items),
                )
            )

        return google_photos_content

    def download_album(
        self, album: Album, num_threads: int = 8
    ) -> List[GooglePhotosContent]:
        media_items = self.search_non_archived_album_media_items(album)
        google_photos_content = self.download_media_items(
            media_items,
            f"Downloading {album.title}",
            num_threads=num_threads,
        )
        return google_photos_content
