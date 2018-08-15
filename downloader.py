import os
from pytube import YouTube

from converter import Converter

class Downloader:
    def __init__(self, url):
        self.yt = YouTube(url)
        self.yt.register_on_complete_callback(self.convert_to_mp3)
        self.stream = self.yt.streams.first()
        self.converter = Converter(self.filename)

    def download(self):
        self.stream.download()

    def convert_to_mp3(self, stream, file_handle):
        self.converter.export()
        self.remove()

    def remove(self):
        os.remove(self.filename)

    @property
    def filename(self):
        return self.stream.default_filename
