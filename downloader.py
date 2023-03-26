import subprocess
import os
from pytube import YouTube
import json
from pathlib import Path

def get_paths():
    with open("paths.json", "r") as f:
        paths = json.load(f)
        path_dict = {
            "vlc_file_path": paths["VLC_FILE_PATH"],
            "video_file_path": paths["VIDEO_FILE_PATH"],
            "video_filename": paths["VIDEO_FILENAME"],
            "video_thumbnail": paths["THUMBNAIL"],
            "latest_download": paths["LATEST_DOWNLOAD"]
        }
    return path_dict

def youtube_download(video_url):
    youtube_obj = YouTube(video_url)
    thumbnail = youtube_obj.thumbnail_url
    youtube_obj = youtube_obj.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

    path_dict = get_paths()
    destination_dir = r"{}".format(path_dict["video_file_path"])
    filename = r"{}.mp4".format(path_dict["video_filename"])

    video_filename = path_dict["video_filename"]
    # Check if file already exists and add a number to the filename to differentiate it
    counter = 1
    while os.path.exists(fr"{destination_dir}\{filename}"):
        filename = f"{video_filename}({counter}).mp4"
        counter += 1

    try:
        video_thumbnail = thumbnail
        paths = {
            "VIDEO_FILE_PATH": path_dict["video_file_path"], 
            "VLC_FILE_PATH": path_dict["vlc_file_path"], 
            "VIDEO_FILENAME": video_filename, 
            "THUMBNAIL": video_thumbnail,
            "LATEST_DOWNLOAD": filename
        }
        with open("paths.json", "w") as f:
            json.dump(paths, f)

        print("Downloading..")
        youtube_obj.download(output_path=destination_dir, filename=filename)
    except:
        print("Error in download")
    else:
        print("Download successful")
    
    return

def play_downloaded_video():
    path_dict = get_paths()

    vlc_path = r"{}\vlc.exe".format(Path(path_dict["vlc_file_path"]))
    video_path  = r"{}\{}".format(Path(path_dict["video_file_path"]), path_dict["latest_download"])

    print("Opening video in VLC..")
    subprocess.call([vlc_path, video_path])
