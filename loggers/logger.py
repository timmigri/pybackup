from termcolor import colored


class Logger:
    def __init__(self, prefix, prefix_color='cyan'):
        self.prefix = prefix
        self.prefix_color = prefix_color

    def log(self, msg, is_error=False):
        prefix = colored('[{}]'.format(self.prefix), self.prefix_color)
        print('{}: {}'.format(prefix, msg))

    def log_separator(self):
        sep = '-----------------------------------'
        print(sep)

    def log_total_items_to_upload(self, folders_count, files_count):
        self.log_separator()
        print('Total items to upload: {}. Folders: {}. Files: {}.'.format(
            folders_count + files_count, folders_count, files_count))
        self.log_separator()

    def log_upload_progress(self, count, total, path):
        self.log('U({}/{}) {}'.format(count, total, path))

    def log_total_items_to_delete(self, folders_count, files_count):
        self.log_separator()
        print('Total items to delete: {}. Folders: {}. Files: {}.'.format(
            folders_count + files_count, folders_count, files_count))
        self.log_separator()

    def log_delete_progress(self, count, total, path):
        self.log('D({}/{}) {}'.format(count, total, path))

    def log_all_items_uploaded(self):
        self.log('All items uploaded!')

    def log_all_items_deleted(self):
        self.log('All items deleted!')

    def log_finish_backup(self):
        self.log('Finish backup!')

    def log_download_progress(self, count, total, path, prefix):
        self.log('{} ({}/{}) {}'.format(prefix, count, total, path))
