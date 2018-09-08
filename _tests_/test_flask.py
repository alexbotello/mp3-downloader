import os
import pytest

from server.server import app, stream
from server.tasks import extract_audio

headers = {'Authorization': os.environ['AUTH_TOKEN']}
file = 'Mastodon - Trilobite'
url = 'https://www.youtube.com/watch?v=3YAwu5jKV5M'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client

def test_home_route(client):
    home = client.get('/')
    test = home.get_json()
    assert test == {'msg': "api is running"}

def test_download_route(client):
    mock = {'url': 'https://www.youtube.com/watch?v=sr7QHFK-ZAw'}
    test = client.post(
        '/download', headers=headers, json=mock
    )
    status = test.status_code
    assert test.is_json == True
    assert status == 202

def test_convert_route(client):
    test = client.get(
        f'/convert/{file}', headers=headers
    )
    status = test.status_code
    assert test.is_json == True
    assert status == 202

def test_status_route(client):
    task_id = "9391054b-6719-45cb-b52f-c7a82d99b6r0"
    test = client.get(
        f'/status/download/{task_id}', headers=headers
    )
    data = test.get_json()
    assert test.status_code == 200
    assert data['status'] == 'PENDING'

def test_retrieve_route(client):
    test = client.get(
        f'/retrieve/{file}', headers=headers
    )
    response_headers = test.headers
    assert response_headers.get('Content-disposition') == f'attachment; filename={file}'
    assert test.mimetype == "application/octet-stream"
    assert test.is_json == False

def test_stream_function():
    global file
    for data in stream(file):
        assert data == 'Error streaming audio file'

    audio = extract_audio(url)
    file = audio['file']
    [data for data in stream(file)] # should run without error and delete file when finished
    with pytest.raises(FileNotFoundError):
        os.remove(file)
