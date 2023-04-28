from __future__ import annotations
import time
from typing import List

from pydantic import BaseModel

from google.oauth2.credentials import Credentials  # type: ignore
from googleapiclient.discovery import build, Resource  # type: ignore

from gpsync.google_photos.schemas.albums import (
    Album,
    ListAlbumsRequest,
    ListAlbumsResponse,
)
from gpsync.google_photos.schemas.media_items import (
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
        response = self.client.mediaItems().search(body=request_body.dict(by_alias=True)).execute()
        return SearchMediaItemsResponse(**response)

    def search_all_album_media_items(self, album: Album):
        request = SearchMediaItemsRequest(album_id=album.id, page_size=100)
        response = self.search_media_items(request)
        media_items = response.media_items

        while response.next_page_token is not None:
            request = SearchMediaItemsRequest(page_size=100, page_token=response.next_page_token)
            response = self.search_media_items(request)
            print(response)
            time.sleep(0.1)
            media_items.extend(response.media_items)

        return

    def download_album(self, album: Album):
        pass
