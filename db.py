# A dropbox based database. Basically, we have a key-value store per file in here. The only reason
# we do is because we need the actual files to be downloaded from dropbox anyway, and since this is
# a serverless thing, we need some persistance. We have this one.
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError

from pydantic_settings import BaseSettings

class DropboxSettings(BaseSettings):
    dropbox_path: str = ""
    dropbox_refresh_token: str
    dropbox_app_key: str
    dropbox_app_secret: str


settings = DropboxSettings()  # type: ignore[call-arg]

class DropboxDB:
    def __init__(self, refresh_token: str):
        self.dbx = dropbox.Dropbox(oauth2_refresh_token = refresh_token, app_key = settings.dropbox_app_key, app_secret = settings.dropbox_app_secret)
        self.path = settings.dropbox_path

    def get_token(self):
        self.dbx.check_and_refresh_access_token()

    def get(self, key: str) -> str:
        # Read the file from Dropbox.
        try:
            self.get_token()
            path: str = f"{self.path}/{key}"
            metadata, res = self.dbx.files_download(path)
            return res.content.decode("utf-8").strip()
        except ApiError as e:
            if e.user_message_text:
                print(f"Error: {e.user_message_text}")
            else:
                print(f"Error: {e}")

    def set(self, key: str, value: str):
        # Write the file to exactly that value
        try:
            self.get_token()
            path: str = f"{self.path}/{key}"
            self.dbx.files_upload(
                value.encode("utf-8"),
                path,
                mode=WriteMode("overwrite")
            )
        except ApiError as e:
            if e.user_message_text:
                print(f"Error: {e.user_message_text}")
            else:
                print(f"Error: {e}")
