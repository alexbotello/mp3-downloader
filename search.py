import sys
import time

from youtube import YouTube
from downloader import Downloader


def download_from_file(filename):
    url = "https://www.youtube.com/watch?v="
    with open(filename, 'r') as file:
        songs = (line.rstrip() for line in file.readlines())

    for song in songs:
        results = YouTube(song).search()
        for result in results:
            link = f"{url}{result}"
            dl = Downloader(link)
            try:
                dl.download()
                break
            except KeyError:
                dl.remove()
                time.sleep(1.1)
                continue


if __name__ == "__main__":
    args = sys.argv[1:]
    query = " ".join(args)
    url = "https://www.youtube.com/watch?v="
    results = YouTube(query).search()

    for result in results:
        link = f"{url}{result}"
        dl = Downloader(link)
        try:
            dl.download()
            break
        except KeyError:
            dl.remove()
            time.sleep(1.5)
            continue

