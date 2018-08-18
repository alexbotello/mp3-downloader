# mp3-downloader
downloads audio from youtube into a mp3 file

## YouTube Key
You will need your own API key, you can gain access to one [here](https://developers.google.com/youtube/v3/getting-started)

Create an `.env` file and add your key inside

```
KEY=dsf90sdf90sdf90sdf90sdf
```

## Usage
```
from utils import download_by_query

q = "mastodon march of the fire ants"
download_by_query(q)
```