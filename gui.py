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
gifAnimation = False

# Threading
def ThreadFunction(inputValue):
    window.write_event_value('-START-GIF-','')
    logging.info("Thread: starting download")
    downloader.YouTubeDownload(inputValue)
    logging.info("Thread: download finished")
    window.write_event_value('-STOP-GIF-','')
    logging.info("Thread: finishing")


# icons for Windows and Linux systems
if sys.platform.startswith("win"):
    sys_specific_icon = './assets/img/icon.ico'
else:
    sys_specific_icon = './assets/img/icon.png'


# RegEx for validating correct URL format
def ValidateYouTubeUrl(url):
    pattern = re.compile(r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]{11}$')
    return pattern.match(url) is not None


# RegEx for validating allowed filename format
def ValidateFilename(filename):
    pattern = r'^[a-zA-Z0-9_\.\- ]+$'
    return bool(re.match(pattern, filename))


# get thumbnail and display after download success
def DisplayThumbnail():
    pathDict = downloader.getPaths()
    time.sleep(2)
    try:
        with urllib.request.urlopen(pathDict["video_thumbnail"]) as url:
            image_data = url.read()
            img = Image.open(BytesIO(image_data))
            png_bio = BytesIO()
            img.save(png_bio, format="PNG")
            png_data = png_bio.getvalue()

        window["-IMAGE-"].update(data=png_data)
    except:
        sg.popup('Something went wrong. Cannot display thumbnail.', icon=sys_specific_icon, title='Problem')


def SavePaths(pathName1, pathName2, pathName3, pathName4, newPathName, pathValue):
    with open("paths.json", "r") as f:
        paths = json.load(f)
        path1 = paths[pathName1]
        path2 = paths[pathName2]
        path3 = paths[pathName3]
        path4 = paths[pathName4]

    newPath = values[pathValue]

    paths = {pathName1: path1, pathName2: path2, pathName3: path3, pathName4: path4, newPathName: newPath}
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
        if ValidateFilename(values["-NEW-FILENAME-"]):
            SavePaths("VLC_FILE_PATH", "VIDEO_FILE_PATH", "THUMBNAIL", "LATEST_DOWNLOAD", "VIDEO_FILENAME", "-NEW-FILENAME-")
        else:
            sg.popup('Invalid filename! Use only alphanumeric characters, underscores, hyphens, periods and/or spaces', icon=sys_specific_icon, title='Problem')

    if event == "-VIDEO-FOLDER-":
        SavePaths("VLC_FILE_PATH", "VIDEO_FILENAME", "THUMBNAIL", "LATEST_DOWNLOAD", "VIDEO_FILE_PATH", "-VIDEO-FOLDER-")

    if event == "-VLC-FOLDER-":
        SavePaths("VIDEO_FILE_PATH", "VIDEO_FILENAME", "THUMBNAIL", "LATEST_DOWNLOAD", "VLC_FILE_PATH", "-VLC-FOLDER-")

    if event == "-BUTTON-KEY-" and values["-IN-"] == True:
        if ValidateYouTubeUrl(values["-INPUT-"]):

            inputValue = values["-INPUT-"]
            logging.info("Main: creating thread")
            threading.Thread(target=ThreadFunction, args=(inputValue,), daemon=True).start()
        else:
            sg.popup('Download failed: Invalid YouTube URL', icon=sys_specific_icon, title='Problem')

    if event == "-BUTTON-KEY-" and values["-IN-"] != True:
        if ValidateYouTubeUrl(values["-INPUT-"]):
            
            inputValue = values["-INPUT-"]
            logging.info("Main: creating thread")
            threading.Thread(target=ThreadFunction, args=(inputValue,), daemon=True).start()
        else:
            sg.popup('Download failed: Invalid YouTube URL', icon=sys_specific_icon, title='Problem')

    if event == "-START-GIF-":
        gifAnimation = True

    if event == "-STOP-GIF-":
        logging.info("Main: stopping gif")
        gifAnimation = False
        window.write_event_value('-DONE-','')

    if gifAnimation:
       sg.popup_animated('./assets/img/animatedFrames.gif', time_between_frames=500)
    else:
       sg.popup_animated(None)
       
    if event == "-DONE-" and values["-IN-"] != True:
        DisplayThumbnail()
        sg.popup('Download successful!', icon=sys_specific_icon, title='Success')

    if event == "-DONE-" and values["-IN-"] == True:
        DisplayThumbnail()
        sg.popup('Download successful! Starting VLC..', icon=sys_specific_icon, title='Success')
        try:
            downloader.PlayDownloadedVideo()
        except:
            sg.popup("VLC.exe could not be found! Check Path Options", icon=sys_specific_icon, title='Problem')

window.close()