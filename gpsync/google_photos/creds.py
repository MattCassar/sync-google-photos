import os
import pickle
from typing import Optional

from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore

from gpsync.utils import create_directories  # type: ignore

SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.readonly",  # Read Only Photos Library API
]



def fetch_or_load_credentials(
    client_secrets_file_path: str, cache_filepath: Optional[str] = None
) -> Credentials:
    if cache_filepath is not None:
        if os.path.exists(cache_filepath):
            credentials = load_credentials(cache_filepath)
            if credentials.valid:
                return credentials
        else:
            create_directories(cache_filepath)

    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file_path, SCOPES)
    credentials = flow.run_local_server()

    if cache_filepath is not None:
        cache_credentials(credentials, cache_filepath)

    return credentials


def load_credentials(cache_filepath: str) -> Credentials:
    with open(cache_filepath, "rb") as file:
        credentials = pickle.load(file)

    return credentials


def cache_credentials(credentials: Credentials, cache_filepath: str):
    with open(cache_filepath, "wb") as file:
        pickle.dump(credentials, file)
