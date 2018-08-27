# mp3-downloader
Downloads audio from youtube into a mp3 file

Primarily a flask back-end server, but does provide a couple utility functions for command line use.

### Command Line Use
- You will need access to a Google YouTube API key. You can create one [here](https://developers.google.com/youtube/v3/getting-started)

Create an `.env` file and add your key inside

```
KEY=dsf90sdf90sdf90sdf90sdf
```

#### Usage
```
from utils import download_by_query

q = "mastodon march of the fire ants"
download_by_query(q)
```