# mp3-downloader
downloads audio from youtube into a mp3 file

## YouTube Key
You will need your own API key, you can gain access to one [here](https://developers.google.com/youtube/v3/getting-started)

Create an `.env` file and add your key inside

```
KEY=dsf90sdf90sdf90sdf90sdf
```

## Usage
1. Download repository and install dependencies
    ```
    pipenv install
    ```
2. Open your virtual environment after installation
    ```
    pipenv shell
    ```
3. Run the search script with song title as an argument
    ```
    python search.py mastodon march of the fire ants
    ```
