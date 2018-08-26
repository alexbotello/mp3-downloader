import os
import logging

from pytube import YouTube
from pydub import AudioSegment


class Downloader:
    def __init__(self, url=None):
        if url:
            self.yt = YouTube(url)
            self.yt.register_on_complete_callback(self.is_complete)
            self.stream = self.yt.streams.first()
            self._file = None
        self.logger = self.configure_logging()
        self.complete = False

    def configure_logging(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def download(self):
        self.logger.info(f"Downloading {self.default_name}")
        self.stream.download()

    # def convert_to_mp3(self, stream, file_handle):
    #     self.export(self.default_name)
    #     self.remove()
    def is_complete(self, stream, file_handle):
        self.logger.info('Download is complete')
        self.complete = True

    def export(self, file_handle):
        # self._file = self.default_name.split('.')[0] + ".mp3"
        self._file = file_handle.split('.')[0] + ".mp3"
        try:
            audio = AudioSegment.from_file(file_handle)
            audio.export(self._file, format="mp3", bitrate="128k")
            self.logger.info(f"Successfully converted {file_handle}")
            self.remove(file_handle)
            return self._file
        except KeyError:
            raise ConvertError

    def remove(self, file=None):
        # if self.default_name:
        #     file = self.default_name
        self.logger.info(f"Removing file `{file}`\n")
        os.remove(file)

    @property
    def default_name(self):
        if self.stream is None:
            return None
        return self.stream.default_filename

    @property
    def title(self):
        return self.yt.title

    @property
    def file(self):
        if self._file:
            return self._file
        return None


class ConvertError(Exception):
    """
    Throws when file fails to convert
    """
    pass