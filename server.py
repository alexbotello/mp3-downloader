import os
import time
import functools
import subprocess

import redis
import youtube_dl
from celery import Celery
from flask_cors import CORS
from flask import Flask, Response, jsonify, request, url_for


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['REDIS_URL'] #url
app.config['CELERY_RESULT_BACKEND'] = os.environ['REDIS_URL'] #url
CORS(app)

celery = Celery(
    app.name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
celery.conf.update(app.config)

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

@app.route('/download', methods=['POST'])
@requires_authorization
def download():
    url = request.get_json()['url']
    task = download_youtube_audio.apply_async(args=[url])
    return jsonify({'Location': url_for('download_status', task_id=task.id)}), 202

@celery.task
def download_youtube_audio(url):
    options = {
    "format":"bestaudio[ext=m4a]",
    "extractaudio": True,
    "quiet": True,
    "ignoreerrors": False,
    "outtmpl": "%(title)s.%(ext)s"
    }
    with youtube_dl.YoutubeDL(options) as ytdl:
        start = time.time()
        result = ytdl.extract_info(url, download=True)
        file = result['title'] + ".m4a"
        end = time.time()
        print(f"Download took {end-start} seconds")
    return {'file': file, 'status': 'Task completed!'}

@app.route('/download/status/<task_id>', methods=['GET'])
@requires_authorization
def download_status(task_id):
    task = download_youtube_audio.AsyncResult(task_id)
    data = task.get()
    response = {'state': task.state}
    response.update(data)
    return jsonify(response)

@app.route('/convert/<file>', methods=['GET'])
@requires_authorization
def convert(file):
    task = m4a_to_mp3.apply_async(args=[file])
    return jsonify({
        'Location': url_for('conversion_status', task_id=task.id)
    }), 202

@celery.task()
def m4a_to_mp3(file):
    outfile = file.split('.')[0] + '.mp3'
    start = time.time()
    subprocess.call(
        f"ffmpeg -i '{file}' -acodec libmp3lame -ab 128k -aq 2 -loglevel quiet '{outfile}'",
        shell=True
    )
    delete_audio_file(file)
    end = time.time()
    print(f'Conversion took {end-start} seconds')
    return {'file': outfile, 'status': 'Task completed!'}

@app.route('/convert/status/<task_id>')
@requires_authorization
def conversion_status(task_id):
    task = m4a_to_mp3.AsyncResult(task_id)
    # data = task.get()
    response = {'state': task.state}
    # response.update(data)
    return jsonify(response)

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