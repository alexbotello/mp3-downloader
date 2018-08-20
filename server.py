import os
import time
import json
import functools

from flask import Flask, send_file, jsonify, request
from flask_cors import CORS

from downloader import Downloader, ConvertError
from utils import download_by_query

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
    try:
        audio.download()
        response = send_file(
            audio.file,
            mimetype="audio/mpeg",
            as_attachment=True,
            attachment_filename=audio.file
        )
    except ConvertError:
        audio = download_by_query(audio.title)
        response = send_file(
            audio.file,
            mimetype="audio/mpeg",
            as_attachment=True,
            attachment_filename=audio.file
        )
    finally:
        response.headers['Content-Type'] = 'audio/mpeg'
        os.remove(audio.file)
        return response



if __name__ == "__main__":
    app.run()