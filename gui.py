import PySimpleGUI as sg
from PIL import Image
from io import BytesIO
import urllib.request
import sys
import re
import json
import threading
import logging
import time

import downloader

sg.theme("DarkGreen4")
gif_animation = False

# Threading
def thread_function(input_value):
    window.write_event_value('-START-GIF-','')
    logging.info("Thread: starting download")
    downloader.youtube_download(input_value)
    logging.info("Thread: download finished")
    window.write_event_value('-STOP-GIF-','')
    logging.info("Thread: finishing")


# icons for Windows and Linux systems
if sys.platform.startswith("win"):
    sys_specific_icon = './assets/img/icon.ico'
else:
    sys_specific_icon = './assets/img/icon.png'


# RegEx for validating correct URL format
def validate_youtube_url(url):
    pattern = re.compile(r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]{11}$')
    return pattern.match(url) is not None


# RegEx for validating allowed filename format
def validate_filename(filename):
    pattern = r'^[a-zA-Z0-9_\.\- ]+$'
    return bool(re.match(pattern, filename))


# get thumbnail and display after download success
def display_thumbnail():
    path_dict = downloader.get_paths()
    time.sleep(2)
    try:
        with urllib.request.urlopen(path_dict["video_thumbnail"]) as url:
            image_data = url.read()
            img = Image.open(BytesIO(image_data))
            png_bio = BytesIO()
            img.save(png_bio, format="PNG")
            png_data = png_bio.getvalue()

        window["-IMAGE-"].update(data=png_data)
    except:
        sg.popup('Something went wrong. Cannot display thumbnail.', icon=sys_specific_icon, title='Problem')


def save_paths(path_name1, path_name2, path_name3, path_name4, new_path_name, path_value):
    with open("paths.json", "r") as f:
        paths = json.load(f)
        path1 = paths[path_name1]
        path2 = paths[path_name2]
        path3 = paths[path_name3]
        path4 = paths[path_name4]

    new_path = values[path_value]

    paths = {path_name1: path1, path_name2: path2, path_name3: path3, path_name4: path4, new_path_name: new_path}
    with open("paths.json", "w") as f:
        json.dump(paths, f)


# ---------------------------------------------------------------------------------------------------------------------------------------|
# COLUMN DEFINITIONS

thumbnail_column = [
    [sg.Image('./assets/img/greetImg.png', key="-IMAGE-", size=(640,480))],
    [sg.Text('Enter YouTube video URL'), sg.InputText(key='-INPUT-'), sg.Button('Ok', key='-BUTTON-KEY-')],
]

options_column = [
    [sg.Button('Exit Program', key='-CLOSE-'), sg.Push()],
    [sg.VPush(), sg.Text(' ')],
    [sg.Image('./assets/img/rightFileOptionsDivider.png')],
    [sg.Text('Filename for downloaded video:')],
    [sg.InputText(size=(30,1), key='-NEW-FILENAME-'), sg.Button('Submit', key='-SUBMIT-FILENAME-')],
    [sg.Checkbox('Open downloaded video in VLC', key='-IN-')],
    [sg.VPush(), sg.Text(' ')],
    [sg.Image('./assets/img/rightPathOptionsDivider.png')],
    [
        sg.Text('Download destination folder'),
        sg.Push(),
    ],
    [
        sg.In(size=(25,1), enable_events=True, key="-VIDEO-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text('Location folder of VLC.exe'),
        sg.Push(),
    ],
    [
        sg.In(size=(25,1), enable_events=True, key="-VLC-FOLDER-"),
        sg.FolderBrowse(),
    ],
]

# ---------------------------------------------------------------------------------------------------------------------------------------|
# LAYOUT DEFINITIONS

layout = [
    [
        sg.Column(thumbnail_column),
        sg.VSeperator(),
        sg.Column(options_column, expand_y='true'),
    ]
]

window = sg.Window('LazyUndulat', layout, icon=sys_specific_icon)

# ---------------------------------------------------------------------------------------------------------------------------------------|
# EVENT LOOP

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt="%H:%M:%S")


while True:
    event, values = window.read(10)
    if event == sg.WIN_CLOSED or event == "-CLOSE-":
        break
    
    if event == "-SUBMIT-FILENAME-":
        if validate_filename(values["-NEW-FILENAME-"]):
            save_paths("VLC_FILE_PATH", "VIDEO_FILE_PATH", "THUMBNAIL", "LATEST_DOWNLOAD", "VIDEO_FILENAME", "-NEW-FILENAME-")
        else:
            sg.popup('Invalid filename! Use only alphanumeric characters, underscores, hyphens, periods and/or spaces', icon=sys_specific_icon, title='Problem')

    if event == "-VIDEO-FOLDER-":
        save_paths("VLC_FILE_PATH", "VIDEO_FILENAME", "THUMBNAIL", "LATEST_DOWNLOAD", "VIDEO_FILE_PATH", "-VIDEO-FOLDER-")

    if event == "-VLC-FOLDER-":
        save_paths("VIDEO_FILE_PATH", "VIDEO_FILENAME", "THUMBNAIL", "LATEST_DOWNLOAD", "VLC_FILE_PATH", "-VLC-FOLDER-")

    if event == "-BUTTON-KEY-" and values["-IN-"] == True:
        if validate_youtube_url(values["-INPUT-"]):

            input_value = values["-INPUT-"]
            logging.info("Main: creating thread")
            threading.Thread(target=thread_function, args=(input_value,), daemon=True).start()
        else:
            sg.popup('Download failed: Invalid YouTube URL', icon=sys_specific_icon, title='Problem')

    if event == "-BUTTON-KEY-" and values["-IN-"] != True:
        if validate_youtube_url(values["-INPUT-"]):
            
            input_value = values["-INPUT-"]
            logging.info("Main: creating thread")
            threading.Thread(target=thread_function, args=(input_value,), daemon=True).start()
        else:
            sg.popup('Download failed: Invalid YouTube URL', icon=sys_specific_icon, title='Problem')

    if event == "-START-GIF-":
        gif_animation = True

    if event == "-STOP-GIF-":
        logging.info("Main: stopping gif")
        gif_animation = False
        window.write_event_value('-DONE-','')

    if gif_animation:
       sg.popup_animated('./assets/img/animatedFrames.gif', time_between_frames=500)
    else:
       sg.popup_animated(None)
       
    if event == "-DONE-" and values["-IN-"] != True:
        display_thumbnail()
        sg.popup('Download successful!', icon=sys_specific_icon, title='Success')

    if event == "-DONE-" and values["-IN-"] == True:
        display_thumbnail()
        sg.popup('Download successful! Starting VLC..', icon=sys_specific_icon, title='Success')
        try:
            downloader.play_downloaded_video()
        except:
            sg.popup("VLC.exe could not be found! Check Path Options", icon=sys_specific_icon, title='Problem')

window.close()