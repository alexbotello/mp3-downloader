import os
import logging

from pytube import YouTube


class Downloader:
    def __init__(self, url):
        self.yt = YouTube(url)
        self.yt.register_on_complete_callback(self.is_complete)
        self.stream = self.yt.streams.filter(subtype='mp4').first()
        self.logger = self.configure_logging()
        self._complete = False

    def configure_logging(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def download(self):
        self.logger.info(f"Downloading {self.filename}")
        self.stream.download()

    def is_complete(self, stream, file_handle):
        self._complete = True
        self.logger.info('Download is complete')

    @property
    def complete(self):
        return self._complete

    @property
    def filename(self):
        if self.stream is None:
            return None
        return self.stream.default_filename
