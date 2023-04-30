import os

def create_directories(filepath: str) -> None:
    directories = "/".join(filepath.split("/")[:-1])
    if directories:
        os.makedirs(directories, exist_ok=True)
