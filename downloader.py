import subprocess
import os
from pytube import YouTube
import json
from pathlib import Path

def getPaths():
    with open("paths.json", "r") as f:
        paths = json.load(f)
        pathDict = {
            "vlc_file_path": paths["VLC_FILE_PATH"],
            "video_file_path": paths["VIDEO_FILE_PATH"],
            "video_filename": paths["VIDEO_FILENAME"],
            "video_thumbnail": paths["THUMBNAIL"],
            "latest_download": paths["LATEST_DOWNLOAD"]
        }
    return pathDict

def YouTubeDownload(videoUrl):
    youtubeObj = YouTube(videoUrl)
    thumbnail = youtubeObj.thumbnail_url
    youtubeObj = youtubeObj.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

    pathDict = getPaths()
    destination_dir = r"{}".format(pathDict["video_file_path"])
    filename = r"{}.mp4".format(pathDict["video_filename"])

    video_filename = pathDict["video_filename"]
    # Check if file already exists and add a number to the filename to differentiate it
    counter = 1
    while os.path.exists(fr"{destination_dir}\{filename}"):
        filename = f"{video_filename}({counter}).mp4"
        counter += 1

    try:
        video_thumbnail = thumbnail
        paths = {
            "VIDEO_FILE_PATH": pathDict["video_file_path"], 
            "VLC_FILE_PATH": pathDict["vlc_file_path"], 
            "VIDEO_FILENAME": video_filename, 
            "THUMBNAIL": video_thumbnail,
            "LATEST_DOWNLOAD": filename
        }
        with open("paths.json", "w") as f:
            json.dump(paths, f)

        print("Downloading..")
        youtubeObj.download(output_path=destination_dir, filename=filename)
    except:
        print("Error in download")
    else:
        print("Download successful")
    
    return

def PlayDownloadedVideo():
    pathDict = getPaths()

    vlc_path = r"{}\vlc.exe".format(Path(pathDict["vlc_file_path"]))
    video_path  = r"{}\{}".format(Path(pathDict["video_file_path"]), pathDict["latest_download"])

    print("Opening video in VLC..")
    subprocess.call([vlc_path, video_path])
