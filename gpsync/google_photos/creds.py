import pickle
from typing import Optional

from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore

SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.readonly",  # Read Only Photos Library API
]


def load_credentials(
    client_secrets_file_path: str, cache_filepath: Optional[str] = None
) -> Credentials:
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file_path, SCOPES)
    credentials = flow.run_local_server()

    if cache_filepath is not None:
        cache_credentials(credentials, cache_filepath)

    return credentials


def cache_credentials(credentials: Credentials, filepath: str):
    with open(filepath, "wb") as file:
        pickle.dump(credentials, file)
