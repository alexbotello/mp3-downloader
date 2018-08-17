import sys
import time

from client import GoogleAPI
from downloader import Downloader, ConvertError


def download_from_file(filename):
    url = "https://www.youtube.com/watch?v="
    with open(filename, 'r') as file:
        songs = (line.rstrip() for line in file.readlines())

    for song in songs:
        results = GoogleAPI().search(song)
        for result in results:
            link = f"{url}{result}"
            audio = Downloader(link)
            try:
                audio.download()
                break
            except ConvertError:
                audio.remove()
                continue
        time.sleep(1.5)


def download_by_query(query):
    url = "https://www.youtube.com/watch?v="
    results = GoogleAPI().search(query)

    for result in results:
        link = url + result
        audio = Downloader(link)
        try:
            audio.download()
            break
        except ConvertError:
            audio.remove()
            continue
    return audio
