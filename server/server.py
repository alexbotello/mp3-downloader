import os
import time
import functools
import subprocess

import youtube_dl
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from downloader import Downloader
from converter import Converter

app = Flask(__name__)
CORS(app)

options = {
    "format":"bestaudio[ext=m4a]",
    "extractaudio": True,
    "quiet": True,
    "ignoreerrors": False,
    "outtmpl": "%(title)s.%(ext)s"
}

def authenticate():
    message = {'error': "Authentication is required."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'
    return resp

def requires_authorization(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        token = os.environ['AUTH_TOKEN']
        if not auth or auth != token:
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': "api is running"})

@app.route('/download', methods=['GET'])
@requires_authorization
def download():
    url = request.args.get('url')
    # audio = Downloader(url)
    # audio.download()
    # while True:
    #     if audio.complete:
    #         return jsonify({'file': audio.filename})
    #     continue
    with youtube_dl.YoutubeDL(options) as ytdl:
        start = time.time()
        result = ytdl.extract_info(url, download=True)
        file = result['title'] + ".m4a"
        end = time.time()
        print(f"Download took {end-start} seconds")
        return jsonify({"file": file})

@app.route('/convert/<file>', methods=['GET'])
@requires_authorization
def convert(file):
    outfile = file.split('.')[0] + '.mp3'
    start = time.time()
    # audio = Converter(file)
    # file = audio.export()
    subprocess.call(
        f"ffmpeg -i '{file}' -acodec libmp3lame -ab 128k -aq 20 -loglevel quiet '{outfile}'",
        shell=True
    )
    delete_audio_file(file)
    end = time.time()
    print(f'Conversion took {end-start} seconds')
    return jsonify({'file': outfile})

@app.route('/retrieve/<file>', methods=['GET'])
@requires_authorization
def send_file(file):
    return Response(
        generate(file),
        mimetype="audio/mpeg",
        content_type="application/octet-stream",
        headers={"Access-Control-Expose-Headers": "Content-Disposition",
                 "Content-disposition": f"attachment; filename={file}"}
    )

def generate(file):
    with open(file, 'rb') as mp3:
        yield '<br/>'
        data = mp3.read(1024)
        while data:
            yield data
            data = mp3.read(1024)
    delete_audio_file(file)

def delete_audio_file(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        print('Audio file does not exist')
        return


if __name__ == "__main__":
    app.run()