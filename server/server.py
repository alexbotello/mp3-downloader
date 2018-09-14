import os
import functools

from flask_cors import CORS
from flask import Flask, Response, jsonify, request, url_for

try:
    import tasks
except ModuleNotFoundError:
    import server.tasks as tasks

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

@app.route('/download', methods=['POST'])
@requires_authorization
def download():
    url = request.get_json()['url']
    task = tasks.extract_audio.delay(url)
    return jsonify({
        'Location': url_for('status', type='download', task_id=task.id),
    }), 202

@app.route('/convert/<file>', methods=['GET'])
@requires_authorization
def convert(file):
    task = tasks.m4a_to_mp3.delay(file)
    return jsonify({
        'Location': url_for('status', type="convert", task_id=task.id),
    }), 202

@app.route('/status/<type>/<task_id>', methods=['GET'])
@requires_authorization
def status(type, task_id):
    """
    Checks status of celery task and return result
    when ready
    """
    response = {}
    celery = ( tasks.extract_audio if type is 'download'
        else tasks.m4a_to_mp3
    )
    task = celery.AsyncResult(task_id)
    if task.ready():
        data = task.get()
        if data['status'] == 'FAILED':
            response['status'] = data['status']
        else:
            response.update(data)
    else:
        response['status'] = task.state
    return jsonify(response)
