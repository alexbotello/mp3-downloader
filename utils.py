import os

import youtube_dl
from pydub import AudioSegment


def extract_audio(url):
    """
    Extracts m4a audio from youtube video
    """
    options = {
        "format": "bestaudio[ext=m4a]",
        "extractaudio": True,
        "quiet": True,
        "ignoreerrors": False,
        "outtmpl": "%(title)s.%(ext)s",
    }
    try:
        print(url)
        with youtube_dl.YoutubeDL(options) as ytdl:
            result = ytdl.extract_info(url, download=True)
            print(result)
            file = result["title"] + ".m4a"
        # state[task_id] = {"file": file, "status": "Complete"}
        return {"file": file, "status": "Complete"}
    except youtube_dl.utils.DownloadError:
        print("error")
        # state[task_id] = {"status": "Failed"}
        return {"status": "Failed"}


def m4a_to_mp3(file, id=None, state=None):
    """
    Converts from m4a to mp3 using ffmpeg
    """
    try:
        outfile = file.split(".")[0] + ".mp3"
        sound = AudioSegment.from_file(file)
        sound.export(outfile, format="mp3")
        state.update(id, {"file": outfile, "status": "Complete"})
    except Exception as e:
        print(e)
        state.update(id, {"status": "Failed"})


def delete_files(file):
    try:
        os.remove(file)
    except FileNotFoundError:
        error = "Audio file does not exist"
        print(error)
        return error

if __name__ == "__main__":
    extract_audio("https://www.youtube.com/watch?v=ZL4MGwlZuAc")
