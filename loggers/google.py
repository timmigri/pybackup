from .logger import Logger


class GoogleLogger(Logger):
    def log_error(self, msg, path, e):
        self.log_separator()
        self.log('{} "{}"'.format(msg, path), True)
        self.log('Error: {}'.format(e))
        self.log_separator()

    def log_error_create_folder(self, path, e):
        self.log_error('Error when create folder', path, e)

    def log_error_delete_folder(self, path, e):
        self.log_error('Error when delete folder', path, e)

    def log_error_create_file(self, path, e):
        self.log_error('Error when create file', path, e)

    def log_error_update_file(self, path, e):
        self.log_error('Error when update file', path, e)

    def log_error_delete_file(self, path, e):
        self.log_error('Error when delete file', path, e)
