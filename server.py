import os
import time
import json
import functools

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from downloader import Downloader, ConvertError
from utils import download_by_query

app = Flask(__name__)
CORS(app)

# def authenticate():
#     message = {'error': "Authentication is required."}
#     resp = jsonify(message)

#     resp.status_code = 401
#     resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'
#     return resp

# def requires_authorization(f):
#     @functools.wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.headers.get('Authorization')
#         token = os.environ['AUTH_TOKEN']
#         if not auth or auth != token:
#             return authenticate()
#         return f(*args, **kwargs)
#     return decorated

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': "api is running"})

@app.route('/download', methods=['GET'])
# @requires_authorization
def stream_mp3():
    url = request.args.get('url')
    file = download_from_youtube(url)

    def generate():
        with open(file, "rb") as mp3:
            data = mp3.read(1024)
            while data:
                yield data
                data = mp3.read(1024)
        delete_audio_file(file)

    return Response(
        generate(),
        mimetype="audio/mpeg",
        headers={"Content-Disposition":
                 f"attachment; filename={file}",
                 "Content-Type": "application/octet-stream"})


def download_from_youtube(url):
    audio = Downloader(url)
    try:
        audio.download()
    except ConvertError:
        audio = download_by_query(audio.title)
    return audio.file


def delete_audio_file(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        print('ERRORING INSIDE GENERATE')
        return


if __name__ == "__main__":
    app.run()