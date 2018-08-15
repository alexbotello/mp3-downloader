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

    def configure_logging(self):
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def download(self):
        self.logger.info(f"Starting download of {self.filename}")
        self.stream.download()

    def convert_to_mp3(self, stream, file_handle):
        self.export(self.filename)
        self.remove()
        self.logger.info(f"Successfully downloaded and converted {self.yt.title}")

    def export(self, file_handle):
        file = self.filename.split('.')[0] + ".mp3"
        try:
            audio = AudioSegment.from_file(file_handle)
            audio.export(file, format="mp3", bitrate="128k")
        except KeyError:
            raise ConvertError

    def remove(self):
        self.logger.info(f"Removing file `{self.filename}`")
        os.remove(self.filename)

    @property
    def filename(self):
        return self.stream.default_filename


class ConvertError(Exception):
    """
    Throws when file fails to convert to mp3
    """
    pass