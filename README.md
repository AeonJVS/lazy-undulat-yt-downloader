# Lazy Undulat Youtube Downloader
A YouTube Downloader written in Python with a GUI built with PySimpleGUI. Offers an easy and quick way to download videos via URL, specify download destination and optionally a path to VLC for immediate playback.

![gui-screenshot](https://user-images.githubusercontent.com/64533217/227733286-55d67717-d80d-42b8-87f8-77c8529608ad.png)

## Installation
Simply clone the repository and test the executable "gui.exe".

## Quick Instructions
1. Launch "gui.exe".
2. Copy a YouTube video URL.
3. Input URL at the bottom left of application window.
4. Click "Ok".

## Application Options

### File Options
- You may change the filename of the video to be downloaded.
- Specify whether or not you wish for the video file to be opened immediately in VLC by checking the box

### Path Options
- Click "Browse" and select where you wish the video file to end up. (Default: "videos" -folder)
- Click "Browse" and select the location of your VLC.exe. (Default: "C:/Program Files/VideoLAN/VLC")
*Heads up: inputting text in the path options instead of using FileBrowse might cause problems, as each keystroke will trigger an event that changes the path specified in paths.json -file.*

