from .logger import Logger


class YandexLogger(Logger):
    def log_error(self, msg, path, response):
        self.log_separator()
        self.log('{} "{}"'.format(msg, path), True)
        self.log('Response code: {}'.format(response.status_code))
        self.log('Message: {}'.format(response.text))
        self.log_separator()

    def log_error_create_folder(self, path, response):
        self.log_error('Error when create folder', path, response)

    def log_error_delete_folder(self, path, response):
        self.log_error('Error when delete folder', path, response)

    def log_error_request_upload_file(self, path, response):
        self.log_error(
            'Error when request url for upload file', path, response)

    def log_error_create_file(self, path, response):
        self.log_error('Error when upload file', path, response)

    def log_error_delete_file(self, path, response):
        self.log_error('Error when delete file', path, response)

    def log_error_request_download_file(self, path, response):
        self.log_error(
            'Error when request url for download file', path, response)

    def log_error_download_file(self, path, response):
        self.log_error('Error when download file', path, response)
