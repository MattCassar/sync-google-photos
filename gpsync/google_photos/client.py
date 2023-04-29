from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import io
from typing import List, Optional, Union

import requests
from google.oauth2.credentials import Credentials  # type: ignore
from googleapiclient.discovery import Resource, build  # type: ignore
from PIL import Image
from pydantic import BaseModel
from tqdm import tqdm  # type: ignore


from gpsync.google_photos.schemas.albums import (
    Album,
    ListAlbumsRequest,
    ListAlbumsResponse,
)
from gpsync.google_photos.schemas.media_items import (
    MediaItem,
    SearchMediaItemsRequest,
    SearchMediaItemsResponse,
)
from gpsync.photos.photo import GooglePhoto, GoogleVideo


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
        response = (
            self.client.albums()
            .list(pageSize=request.page_size, pageToken=request.page_token)
            .execute()
        )
        return ListAlbumsResponse(**response)

    def list_all_albums(self) -> List[Album]:
        request = ListAlbumsRequest()
        response = self.list_albums(request)
        albums = response.albums

        while response.next_page_token is not None:
            request = ListAlbumsRequest(page_token=response.next_page_token)
            response = self.list_albums(request)
            albums.extend(response.albums)

        return albums

    def search_media_items(
        self, request_body: SearchMediaItemsRequest
    ) -> SearchMediaItemsResponse:
        response = (
            self.client.mediaItems()
            .search(body=request_body.dict(by_alias=True))
            .execute()
        )
        return SearchMediaItemsResponse(**response)

    def search_all_album_media_items(self, album: Album) -> List[MediaItem]:
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
    ) -> Union[GooglePhoto, GoogleVideo]:
        if media_item.media_metadata.photo is not None:
            download_url = f"{media_item.base_url}=d"
        elif media_item.media_metadata.video is not None:
            download_url = f"{media_item.base_url}=dv"
        else:
            raise ValueError(
                "media_item is neither a photo nor a video, this shouldn't happen."
            )

        response = requests.get(download_url)
        if response.status_code >= 400:
            raise RuntimeError(f"Failed to download media_item {media_item.id}")

        google_photo_or_video: Optional[Union[GooglePhoto, GoogleVideo]] = None
        if media_item.media_metadata.photo is not None:
            image = Image.open(io.BytesIO(response.content))
            google_photo_or_video = GooglePhoto(media_item=media_item, image=image)
        elif media_item.media_metadata.video is not None:
            google_photo_or_video = GoogleVideo(
                media_item=media_item, video=response.content
            )
        else:
            raise ValueError(
                "media_item is neither a photo nor a video, this shouldn't happen."
            )

        return google_photo_or_video

    def download_album(
        self, album: Album, num_threads: int = 8
    ) -> List[Union[GooglePhoto, GoogleVideo]]:
        media_items = self.search_all_album_media_items(album)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            google_photos: List[Union[GooglePhoto, GoogleVideo]] = list(
                tqdm(
                    executor.map(self.download_media_item, media_items),
                    unit=" media items",
                    desc=f"Downloading {album.title}",
                    total=len(media_items),
                )
            )

        return google_photos
