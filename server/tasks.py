import os
import subprocess

import boto3
from botocore.client import Config

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

@celery.task(name="server.tasks.m4a_to_mp3")
def m4a_to_mp3(file):
    """
    Converts from m4a to mp3 using ffmpeg
    """
    try:
        outfile = file.split('.')[0] + '.mp3'
        sound = AudioSegment.from_file(file)
        sound.export(outfile, format="mp3")
        url = upload_file_to_s3(outfile)
        return {'file': outfile, 'status': 'SUCCESS', 'url': url}
    except Exception as e:
        print(e)
        return {'status': 'FAILED'}
    finally:
        delete_files([file, outfile])

def upload_file_to_s3(file):
    s3 = boto3.client('s3', config=Config(
        s3={'addressing_style': 'path'}, signature_version='s3v4')
    )
    bucket = 'mp3-download-storage'
    s3.upload_file(file, bucket, file)

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': file,
            "ResponseContentDisposition": f"attachment; filename={file}",
            "ResponseContentType" : "application/octet-stream"
        },
        ExpiresIn=500
    )
    return url

def delete_files(files):
    try:
        for file in files:
            os.remove(file)
    except FileNotFoundError:
        error = 'Audio file does not exist'
        print(error)
        return error
