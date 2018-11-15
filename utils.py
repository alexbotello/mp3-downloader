import os

import youtube_dl
from pydub import AudioSegment


def extract_audio(url, task_id=None, state=None):
    """
    Extracts m4a audio from youtube video
    """
    options = {
        "format": "bestaudio[ext=m4a]",
        "extractaudio": True,
        "quiet": True,
        "ignoreerrors": False,
        "outtmpl": "%(title)s.%(ext)s",
    }
    try:
        with youtube_dl.YoutubeDL(options) as ytdl:
            result = ytdl.extract_info(url, download=True)
            file = result["title"] + ".m4a"
        state[task_id] = {"file": file, "status": "Complete"}
    except youtube_dl.utils.DownloadError:
        state[task_id] = {"status": "Failed"}


def m4a_to_mp3(file, task_id=None, state=None):
    """
    Converts from m4a to mp3 using ffmpeg
    """
    try:
        outfile = file.split(".")[0] + ".mp3"
        sound = AudioSegment.from_file(file)
        sound.export(outfile, format="mp3")
        state[task_id] = {"file": outfile, "status": "Complete"}
    except Exception as e:
        state[task_id] = {"status": "Failed"}
    finally:
        os.remove(file)


async def generate(file):
    with open(file, "rb") as mp3:
        data = mp3.read(1024)
        while data:
            yield data
            data = mp3.read(1024)
    os.remove(file)
