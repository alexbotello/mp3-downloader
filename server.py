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

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': "api is running"})

@app.route('/download', methods=['GET'])
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
        content_type="application/octet-stream",
        headers={"Content-disposition": f"attachment; filename={file}"})


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