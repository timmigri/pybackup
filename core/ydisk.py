# https://oauth.yandex.ru
# https://oauth.yandex.ru/authorize?response_type=token&client_id=PROJECT_ID

import os
import json
import requests
import sys

from pathlib import Path

from core.base import Base
from data.configs import YANDEX_CONFIG as CONFIG
from services.feature import Feature
from loggers.yandex import YandexLogger


API_URLS = {
    'resources': 'https://cloud-api.yandex.net:443/v1/disk/resources?path={}',
    'get_upload_link':
        'https://cloud-api.yandex.net:443/v1/disk/resources/upload?path={}',
    'download':
        'https://cloud-api.yandex.net/v1/disk/resources/download?path={}'
}

API_ERRORS = {
    'folder_exists': 'DiskPathPointsToExistentDirectoryError',
    'file_exists': 'DiskResourceAlreadyExistsError',
    'not_found': 'DiskNotFoundError'
}


class YandexDisc(Base):
    def __init__(self):
        self.config = CONFIG
        self.logger = YandexLogger('Yandex Disc', 'yellow')
        self.token = json.loads(open('auth/yandex/data.json').read())['token']
        super().__init__()

    def run(self):
        self.create_root_folder()
        super().run()

    def is_status_code_success(self, code):
        return code >= 200 and code <= 204

    def get_headers(self):
        return {
            'Authorization': 'OAuth {}'.format(self.token),
        }

    def prepare_path(self, path):
        if path == self.config['sqlite_root_folder']:
            return self.config['root_folder']
        path = path[len(str(Path.home())) + 1:]
        path = os.path.join(
            self.config['root_folder'], path)
        return path

    def create_root_folder(self):
        path = self.config['sqlite_root_folder']
        item = self.sqlite_helper.get_folder_by_path(path)
        if item is None:
            self.create_folder(path)

    def create_folder(self, path):
        pc_path = path
        path = self.prepare_path(path)

        url = API_URLS['resources'].format(path)
        r = requests.put(url, headers=self.get_headers())
        if self.is_status_code_success(r.status_code):
            self.sqlite_helper.create_folder(pc_path)
        else:
            if r.json()['error'] == API_ERRORS['folder_exists']:
                Feature.increment_feature()
                self.sqlite_helper.create_folder(pc_path)
                return
            self.logger.log_error_create_folder(path, r)
            sys.exit(1)

    def delete_folder(self, path):
        pc_path = path
        path = self.prepare_path(path)

        url = API_URLS['resources'].format(path)
        url += '&permanently=true'

        r = requests.delete(url, headers=self.get_headers())
        if self.is_status_code_success(r.status_code):
            self.sqlite_helper.delete_folder(pc_path)
        else:
            if r.json()['error'] == API_ERRORS['not_found']:
                self.sqlite_helper.delete_folder(pc_path)
                return
            self.logger.log_error_delete_folder(path, r)
            sys.exit(1)

    def request_url_for_upload(self, path):
        pc_path = path
        path = self.prepare_path(path)

        url = API_URLS['get_upload_link'].format(path)
        r = requests.get(url, headers=self.get_headers())

        if self.is_status_code_success(r.status_code):
            return r.json()['href']
        else:
            if r.json()['error'] == API_ERRORS['file_exists']:
                Feature.increment_feature()
                self.sqlite_helper.create_file(pc_path)
                return None
            self.logger.log_error_request_upload_file(path, r)
            sys.exit(1)
            return None

    def upload_file(self, path):
        pc_path = path
        path = self.prepare_path(path)

        url = self.request_url_for_upload(pc_path)
        if url is not None:
            files = {
                'file': self.crypter.encrypt(open(pc_path, 'rb').read())
            }
            r = requests.post(url, headers=self.get_headers(), files=files)

            if self.is_status_code_success(r.status_code):
                self.sqlite_helper.create_file(pc_path)
            else:
                self.logger.log_error_create_file(path, r)
                sys.exit(1)

    def delete_file(self, path):
        pc_path = path
        path = self.prepare_path(path)

        url = API_URLS['resources'].format(path)
        url += '&permanently=true'
        r = requests.delete(url, headers=self.get_headers())
        if self.is_status_code_success(r.status_code):
            self.sqlite_helper.delete_file(pc_path)
        else:
            if r.json()['error'] == API_ERRORS['not_found']:
                self.sqlite_helper.delete_file(pc_path)
                return
            self.logger.log_error_delete_file(path, r)
            sys.exit(1)

    def update_file(self, path):
        self.delete_file(path)
        self.upload_file(path)

    def request_url_for_download(self, path):
        path = self.prepare_path(path)
        url = API_URLS['download'].format(path)
        r = requests.get(url, headers=self.get_headers())
        if self.is_status_code_success(r.status_code):
            return r.json()['href']
        else:
            self.logger.log_error_download_file(path, r)
            sys.exit(1)

    def download_file(self, path, save_to):
        url = self.request_url_for_download(path)
        r = requests.get(url)
        if self.is_status_code_success(r.status_code):
            with open(save_to, 'wb') as file:
                file.write(self.crypter.decrypt(r.content))
        else:
            self.logger.log_error_download_file(path, r)
            sys.exit(1)
