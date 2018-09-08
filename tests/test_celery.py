import os
import pytest

from server.tasks import celery, extract_audio, m4a_to_mp3, delete_file

url = 'https://www.youtube.com/watch?v=sr7QHFK-ZAw'
fake_url = 'https://www.youtube.com/watch?v=sr7QHFK-567'
file = None
converted_file = None

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': os.environ['REDIS_URL'],
        'result_backend': os.environ['REDIS_URL']
    }

def test_extract_audio_function():
    global file
    result = extract_audio(url)
    ext = result['file'].split('.')[1]
    file = result['file']
    assert result['status'] == 'SUCCESS'
    assert ext == 'm4a'
    new_result = extract_audio(fake_url)
    assert new_result['status'] == 'FAILED'

def test_extract_audio_celery_integration():
    pass

def test_m4a_to_mp3_function():
    global converted_file
    sound = extract_audio(url)
    file = sound['file']
    result = m4a_to_mp3(file)
    ext = result['file'].split('.')[1]
    converted_file = result['file']
    assert result['status'] == 'SUCCESS'
    assert ext == 'mp3'
    fake_file = 'Metallica - One.m4a'
    result = m4a_to_mp3(fake_file)
    assert result['status'] == 'FAILED'


def test_delete_file():
    global file, converted_file
    name = file
    con = converted_file
    delete_file(file)
    delete_file(converted_file)
    assert os.path.exists(name) == False
    assert os.path.exists(con) == False
    assert delete_file(name) == 'Audio file does not exist'
    assert delete_file(con) == 'Audio file does not exist'
