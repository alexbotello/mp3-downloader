import os
import time
import json
import functools

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from downloader import Downloader
from converter import Converter
# from utils import download_by_query

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': "api is running"})

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    audio = Downloader(url)
    audio.download()
    while True:
        if audio.complete:
            return jsonify({'file': audio.filename})
        else:
            continue

@app.route('/convert', methods=['GET'])
def convert():
    file = request.args.get('file')
    audio = Converter(file)
    file = audio.export()
    def generate():
        with open(file, 'rb') as mp3:
            # yield '<br/>'
            data = mp3.read(1024)
            while data:
                yield data
                data = mp3.read(1024)
        delete_audio_file(file)
    return Response(
        generate(),
        mimetype="audio/mpeg",
        content_type="application/octet-stream",
        headers={"Access-Control-Expose-Headers": "Content-Disposition",
                 "Content-disposition": f"attachment; filename={file}"})


def delete_audio_file(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        print('Audio file does not exist')
        return


if __name__ == "__main__":
    app.run()