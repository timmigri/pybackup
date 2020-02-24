import os
from pathlib import Path

from services.sqlite_helper import SqliteHelper
from services.crypter import Crypter


class Base:
    def __init__(self):
        self.crypter = Crypter()
        # Pathes to upload
        self.upload_folders = []  # array of string
        self.upload_files = []  # array of string
        self.upload_count = 0
        self.delete_count = 0
        self.sqlite_helper = SqliteHelper()
        self.init_sqlite_connection()

    def add_upload_folder(self, path):
        fld = self.sqlite_helper.get_folder_by_path(path)
        # 2 - index of res_id
        if fld is None:
            self.upload_folders.append(path)

    def add_upload_file(self, path):
        file = self.sqlite_helper.get_file_by_path(path)
        lm = self.sqlite_helper.get_file_last_modified(path)
        # 2 - index of res_id
        if file is None or file[3] != lm:
            self.upload_files.append(path)

    def get_sql_folder(self):
        return os.path.join(str(Path.home()), '.backup_data')

    def is_path_in_exclude(self, path):
        for exclude_path in self.config['ignore_pathes']:
            if exclude_path in path:
                return True
        return False

    def increment_upload_count(self, total, path):
        self.upload_count += 1
        self.logger.log_upload_progress(self.upload_count, total, path)

    def increment_delete_count(self, total, path):
        self.delete_count += 1
        self.logger.log_delete_progress(
            self.delete_count, total, path)

    def backup_folders(self, total):
        for path in self.upload_folders:
            fld = self.sqlite_helper.get_folder_by_path(path)
            if fld is None:
                # Call from
                self.create_folder(path)
            self.increment_upload_count(total, path)

    def backup_files(self, total):
        for path in self.upload_files:
            lm = self.sqlite_helper.get_file_last_modified(path)
            file = self.sqlite_helper.get_file_by_path(path)
            if file is None:
                # Call from
                self.upload_file(path)
            elif file[3] != lm:
                # Call from
                self.update_file(path)
            self.increment_upload_count(total, path)

    def backup_items(self):
        upload_folders_count = len(self.upload_folders)
        upload_files_count = len(self.upload_files)
        total_items_count = upload_folders_count + upload_files_count
        if total_items_count == 0:
            self.logger.log_all_items_uploaded()
            return
        self.logger.log_total_items_to_upload(
            upload_folders_count, upload_files_count)
        self.backup_folders(total_items_count)
        self.backup_files(total_items_count)

    def scan_nonexistent_items(self):
        ne_fld_pathes = self.get_nonexistent_folders()
        ne_file_pathes = self.get_nonexistent_files()
        total_nonexistent_count = len(ne_fld_pathes) + len(ne_file_pathes)
        if total_nonexistent_count == 0:
            self.logger.log_all_items_deleted()
            return
        self.logger.log_total_items_to_delete(
            len(ne_fld_pathes), len(ne_file_pathes))
        self.delete_nonexistent_folders(
            ne_fld_pathes, total_nonexistent_count)
        self.delete_nonexistent_files(
            ne_file_pathes, total_nonexistent_count)

    def delete_nonexistent_folders(self, pathes, total):
        for path in pathes:
            # Call from
            self.delete_folder(path)
            self.increment_delete_count(total, path)

    def delete_nonexistent_files(self, pathes, total):
        for path in pathes:
            # Call from
            self.delete_file(path)
            self.increment_delete_count(total, path)

    def get_nonexistent_folders(self):
        ne_fld_pathes = []
        for fld in self.sqlite_helper.get_all_folders():
            path = fld[1]
            # Root folder on disk(not on pc)
            if path == self.config['sqlite_root_folder']:
                continue
            if not os.path.isdir(path) or self.is_path_in_exclude(path):
                ne_fld_pathes.append(path)
        return ne_fld_pathes

    def get_nonexistent_files(self):
        ne_file_pathes = []
        for file in self.sqlite_helper.get_all_files():
            path = file[1]
            if not os.path.isfile(path) or self.is_path_in_exclude(path):
                ne_file_pathes.append(path)
        return ne_file_pathes

    def init_sqlite_connection(self):
        self.sqlite_helper.init_connection(
            self.get_sql_folder(), '{}.sqlite'.format(
                self.config['sqlite_name']))

    def path_walk(self, path):
        for top, dirs, files in os.walk(path):
            for dir in dirs:
                path = os.path.join(top, dir)
                if self.is_path_in_exclude(path):
                    continue
                self.add_upload_folder(path)
            for file in files:
                path = os.path.join(top, file)
                if self.is_path_in_exclude(path):
                    continue
                self.add_upload_file(path)

    def run(self):
        self.scan_nonexistent_items()
        for path in self.config['walk_folders']:
            path = os.path.join(str(Path.home()), path)
            self.add_upload_folder(path)
            self.path_walk(path)
        self.backup_items()
        self.logger.log_finish_backup()

    def download_backup(self):
        path = os.path.join(str(Path.home()), self.config['download_folder'])
        os.makedirs(path, exist_ok=True)
        self.download_folders(path)
        self.download_files(path)

    def download_folders(self, backup_path):
        folders = self.sqlite_helper.get_all_folders()
        count = 0
        folders_count = len(folders)
        for fld in folders:
            count += 1
            path = fld[1]
            self.logger.log_download_progress(
                count, folders_count, path, 'Folders')
            if path == self.config['sqlite_root_folder']:
                continue
            path = path[len(str(Path.home())) + 1:]
            path = os.path.join(backup_path, path)
            os.makedirs(path, exist_ok=True)

    def download_files(self, backup_path):
        files = self.sqlite_helper.get_all_files()
        count = 0
        files_count = len(files)
        for file in files:
            count += 1
            path = file[1]
            self.logger.log_download_progress(
                count, files_count, path, 'Files')
            save_to = path[len(str(Path.home())) + 1:]
            save_to = os.path.join(backup_path, save_to)
            if os.path.isfile(save_to):
                continue
            self.download_file(path, save_to)
