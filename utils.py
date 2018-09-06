import sys
import time

from client import GoogleAPI
from downloader import Downloader
from converter import Converter


def download_from_file(filename):
    url = "https://www.youtube.com/watch?v="
    with open(filename, 'r') as file:
        songs = (line.rstrip() for line in file.readlines())

    for song in songs:
        results = GoogleAPI().search(song)
        for index, result in enumerate(results):
            if index == 0:
                link = url + result
                audio = Downloader(link)
                audio.download()
                converter = Converter(audio.filename)
                converter.export()
                time.sleep(.5)
            else:
                break


def download_by_query(query):
    url = "https://www.youtube.com/watch?v="
    results = GoogleAPI().search(query)

    for index, result in enumerate(results):
        if index == 0:
            link = url + result
            audio = Downloader(link)
            audio.download()
            converter = Converter(audio.filename)
            converter.export()
        else:
            break
