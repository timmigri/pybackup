import io
import os
import json
import sys
import magic

from pathlib import Path

from apiclient.http import MediaIoBaseUpload
from apiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from .base import Base
from data.configs import GOOGLE_CONFIG as CONFIG
from loggers.google import GoogleLogger


class GoogleDrive(Base):
    def __init__(self):
        self.config = CONFIG
        self.logger = GoogleLogger('Google Drive', 'blue')
        self.auth()
        super().__init__()

    def get_credentials(self):
        creds_path = 'auth/google/credentials.json'
        scopes = ['https://www.googleapis.com/auth/drive']

        if os.path.exists(creds_path):
            credentials = Credentials.from_authorized_user_file(
                creds_path, scopes=scopes)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'auth/google/client_secret.json', scopes)
            creds = flow.run_local_server()
            dict_creds = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'id_token': creds.id_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret
            }
            with open(creds_path, 'w') as f:
                f.write(json.dumps(dict_creds))
            credentials = creds

        if credentials.expired:
            credentials.refresh(Request())

        return credentials

    def auth(self):
        self.drive = build('drive', 'v3', credentials=self.get_credentials())

    def run(self):
        self.create_root_folder()

        super().run()

    def create_root_folder(self):
        path = self.config['sqlite_root_folder']
        item = self.sqlite_helper.get_folder_by_path(path)
        if item is None:
            self.create_folder(self.config['sqlite_root_folder'])

    def get_folder_title(self, path):
        if path == self.config['sqlite_root_folder']:
            return self.config['root_folder']
        return os.path.basename(path)

    def get_item_parent_id(self, path):
        if path == self.config['sqlite_root_folder']:
            return None

        parent_folder_path = str(Path(path).parent)
        if parent_folder_path == str(Path.home()):
            parent_folder_path = self.config['sqlite_root_folder']

        fld = self.sqlite_helper.get_folder_by_path(
            parent_folder_path)
        return fld[2]

    def create_folder(self, path):
        body = {
            'name': self.get_folder_title(path),
            'mimeType': 'application/vnd.google-apps.folder'
        }
        parent_folder_id = self.get_item_parent_id(path)
        if parent_folder_id is not None:
            body['parents'] = [parent_folder_id]

        try:
            folder = self.drive.files().create(body=body,
                                               fields='id').execute()
            self.sqlite_helper.create_folder(path, folder['id'])
        except Exception as e:
            self.logger.log_error_create_folder(path, e)
            sys.exit(1)

    def delete_folder(self, path):
        fld = self.sqlite_helper.get_folder_by_path(path)
        try:
            self.drive.files().delete(fileId=fld[2]).execute()
            self.sqlite_helper.delete_folder(path)
        except HttpError as e:
            if e.resp.status == 404:
                self.sqlite_helper.delete_folder(path)
                return
            self.logger.log_error_delete_folder(path, e)
            sys.exit(1)
        except Exception as e:
            self.logger.log_error_delete_folder(path, e)
            sys.exit(1)

    def upload_file(self, path):
        fh = io.BytesIO(self.crypter.encrypt(open(path, 'rb').read()))
        name = os.path.basename(path)
        mimetype = magic.from_file(path, mime=True)
        media = MediaIoBaseUpload(fh, mimetype=mimetype)

        body = {
            'name': name,
        }

        parent_folder_id = self.get_item_parent_id(path)
        if parent_folder_id is not None:
            body['parents'] = [parent_folder_id]

        try:
            file = self.drive.files().create(
                body=body, media_body=media, fields='id'
            ).execute()
            self.sqlite_helper.create_file(path, file['id'])
        except Exception as e:
            self.logger.log_error_create_file(path, e)
            sys.exit(1)

    def update_file(self, path):
        fh = io.BytesIO(self.crypter.encrypt(open(path, 'rb').read()))
        file = self.sqlite_helper.get_file_by_path(path)
        name = os.path.basename(path)
        mimetype = magic.from_file(path, mime=True)
        media = MediaIoBaseUpload(fh, mimetype=mimetype)

        body = {
            'name': name,
        }

        try:
            self.drive.files().update(
                fileId=file[2], body=body, media_body=media, fields='id'
            ).execute()
            self.sqlite_helper.update_file_last_modified(path)
        except Exception as e:
            self.logger.log_error_update_file(path, e)
            sys.exit(1)

    def delete_file(self, path):
        file = self.sqlite_helper.get_file_by_path(path)
        try:
            self.drive.files().delete(fileId=file[2]).execute()
            self.sqlite_helper.delete_file(path)
        except HttpError as e:
            if e.resp.status == 404:
                self.sqlite_helper.delete_file(path)
                return
            self.logger.log_error_delete_file(path, e)
            sys.exit(1)
        except Exception as e:
            self.logger.log_error_delete_file(path, e)
            sys.exit(1)

    def download_file(self, path, save_to):
        file = self.sqlite_helper.get_file_by_path(path)
        request = self.drive.files().get_media(fileId=file[2])
        fh = io.FileIO(save_to, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        with open(save_to, 'rb') as file:
            bytes = file.read()
        with open(save_to, 'wb') as file:
            file.write(self.crypter.decrypt(bytes))
