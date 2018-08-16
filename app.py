import time
import os
from flask import Flask, send_file, jsonify

from client import GoogleAPI
from downloader import Downloader, ConvertError


app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'msg': "api is running"})


@app.route('/download/<query>', methods=['GET'])
def download(query):
    base = "https://www.youtube.com/watch?v="
    results = GoogleAPI().search(query)

    for result in results:
        url = base + result
        dl = Downloader(url)
        try:
            dl.download()
            break
        except ConvertError:
            dl.remove()
            continue

    response = send_file(dl.file)
    os.remove(dl.file)
    response.headers['my-custom-header'] = 'my-custom-status-0'
    return response



if __name__ == "__main__":
    app.run(debug=True)