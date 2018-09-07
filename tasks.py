import os
import subprocess

import redis
import youtube_dl
from celery import Celery

celery = Celery(
    "tasks",
    broker=os.environ['CELERY_URL'],
    backend=os.environ['CELERY_URL']
)

@celery.task
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
        return {'file': file, 'status': 'Task completed!'}
    except Exception as e:
        print(e)
        delete_file(file)

@celery.task()
def m4a_to_mp3(file):
    """
    Converts from m4a to mp3 using ffmpeg
    """
    try:
        outfile = file.split('.')[0] + '.mp3'
        subprocess.call(
            f"ffmpeg -i '{file}' -acodec libmp3lame -ab 128k -aq 2 -loglevel quiet '{outfile}'",
            shell=True
        )
        return {'file': outfile, 'status': 'Task completed!'}
    except Exception as e:
        print(e)
    finally:
        delete_file(file)

def delete_file(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        print('Audio file does not exist')
        return