import os
import logging

from pydub import AudioSegment


class Converter():
    def __init__(self, file):
        self.handle = file
        self.file = file.split('.')[0] + '.mp3'
        self.logger = self.configure_logging()

    def configure_logging(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def export(self):
        try:
            audio = AudioSegment.from_file(self.handle)
            audio.export(self.file, format="mp3")
            self.logger.info(f"Successfully converted {self.handle}")
            self.remove()
            return self.file
        except KeyError:
            self.logger.info('error error')

    def remove(self):
        os.remove(self.handle)
        self.logger.info(f"Removed file {self.handle}")

