from pydub import AudioSegment


class Converter:
    def __init__(self, filename):
        self._name = filename

    def export(self):
        file = self._name.split('.')[0] + ".mp3"
        audio = AudioSegment.from_file(self._name)
        audio.export(file, format="mp3", bitrate="128k")
