import os
import subprocess

import redis
import youtube_dl
from celery import Celery
from pydub import AudioSegment

celery = Celery(
    "tasks",
    broker=os.environ['REDIS_URL'],
    backend=os.environ['REDIS_URL']
)

@celery.task(name='server.tasks.extract_audio')
def extract_audio(url):
    """
    Extracts m4a audio from youtube video
    """
    options = {
    "format":"bestaudio[ext=m4a]",
    "extractaudio": True,
    "quiet": True,
    "ignoreerrors": False,
    "outtmpl": "%(title)s.%(ext)s"
    }
    try:
        with youtube_dl.YoutubeDL(options) as ytdl:
            result = ytdl.extract_info(url, download=True)
            file = result['title'] + ".m4a"
        return {'file': file, 'status': 'SUCCESS'}
    except youtube_dl.utils.DownloadError:
        return {'status': 'FAILED'}
    except Exception as e:
        print(e)
        delete_file(file)

@celery.task(name="server.tasks.m4a_to_mp3")
def m4a_to_mp3(file):
    """
    Converts from m4a to mp3 using ffmpeg
    """
    try:
        outfile = file.split('.')[0] + '.mp3'
        # subprocess.call(
        #     f"ffmpeg -i '{file}' -acodec libmp3lame -ab 128k -aq 2 -loglevel quiet '{outfile}'",
        #     shell=True
        # )
        sound = AudioSegment.from_file(file)
        sound.export(outfile, format="mp3")
        return {'file': outfile, 'status': 'SUCCESS'}
    except Exception as e:
        print(e)
        return {'status': 'FAILED'}
    finally:
        delete_file(file)

def delete_file(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        print('Audio file does not exist')
        return