import os
import logging

from pytube import YouTube
from pydub import AudioSegment


class Downloader:
    def __init__(self, url):
        self.yt = YouTube(url)
        self.yt.register_on_complete_callback(self.convert_to_mp3)
        self.stream = self.yt.streams.first()
        self.logger = self.configure_logging()
        self._file = None

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

    def convert_to_mp3(self, stream, file_handle):
        self.export(self.default_name)
        self.remove()

    def export(self, file_handle):
        self._file = self.default_name.split('.')[0] + ".mp3"
        try:
            audio = AudioSegment.from_file(file_handle)
            audio.export(self._file, format="mp3", bitrate="128k")
            self.logger.info(f"Successfully converted {self.yt.title}")
        except KeyError:
            raise ConvertError

    def remove(self):
        self.logger.info(f"Removing file `{self.default_name}`\n")
        os.remove(self.default_name)

    @property
    def default_name(self):
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