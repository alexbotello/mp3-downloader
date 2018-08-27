import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleAPI:
    def __init__(self):
        key = os.environ['KEY']
        service = "youtube"
        version = "v3"
        self.url = "https://www.youtube.com/watch?v="
        self.yt = build(service, version, developerKey=key)

    def search(self, query, max_results=10, order="relevance"):
        response = self.yt.search().list(
            q=query,
            type="video",
            order=order,
            part="id, snippet",
            maxResults=max_results
        ).execute()

        return(
            result['id']['videoId']
            for result in response.get('items')
        )
