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
            dl = Downloader(link)
            try:
                dl.download()
                break
            except ConvertError:
                dl.remove()
                continue
        time.sleep(1.5)


if __name__ == "__main__":
    args = sys.argv[1:]
    query = " ".join(args)
    url = "https://www.youtube.com/watch?v="
    results = GoogleAPI().search(query)

    for result in results:
        link = f"{url}{result}"
        dl = Downloader(link)
        try:
            dl.download()
            break
        except ConvertError:
            dl.remove()
            continue


