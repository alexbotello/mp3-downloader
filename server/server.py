import os
import time
import functools

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

from downloader import Downloader
from converter import Converter

app = Flask(__name__)
CORS(app)

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
    audio = Downloader(url)
    audio.download()
    while True:
        if audio.complete:
            time.sleep(2)
            return jsonify({'file': audio.filename})
        continue

@app.route('/convert/<file>', methods=['GET'])
@requires_authorization
def convert(file):
    audio = Converter(file)
    file = audio.export()
    def generate():
        with open(file, 'rb') as mp3:
            yield '<br/>'
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