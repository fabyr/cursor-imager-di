# cursor-imager-di

A tool to draw images using your mouse!
Compatible with both Windows and Linux.
On Windows you can choose to use DirectInput (more stable and should work in games) or not.
On Linux xdotool is used to control the mouse.

#### Table of contents
- [Screenshots](#screenshots)
- [Functionality and how it works](#functionality-and-how-it-works)
- [Installation](#installation)
    * [Linux Installation](#linux-installation)
    * [Windows Installation](#windows-installation)
- [Motivation](#motivation)

## Screenshots
Graphical Interface

![Interface](/images/gui1.png)

Test Image

[Creator: TomSka](https://www.youtube.com/Tom)

![Test Image](/images/muffin.png)

Results

![Results](/images/result1.png)

## Functionality and how it works
Any generic image can be loaded, to which, if desired, edge detection is performed, so only lines and not regions are drawn.
After that a path finding algorithm finds a connected path throughout the entire image.
(Or multiple connected paths).
Then with the press of a selectable hotkey your mouse will be controlled according to the processed image, and will hopefully draw something resembling the input image.

After starting the python script you'll be greeted with a Graphical Interace
allowing you to change some settings.
Those include things such as:
- Edge detection
- Speed of cursor movement
- Parameters for controlling the Path-Finding-Algorithm
- ...

## Installation
This program works both on Windows and Linux.
Python 3 is required to be installed on your system. (Tested with Python 3.8.10)

[Python Download](https://www.python.org/downloads/)

### Linux installation
(Tested on Linux Mint 20.3)

System Dependencies:
- xdotool and xclip (install on debian based systems with `sudo apt install xdotool xclip`)
- xclip is needed for loading images from clipboard

```
git clone https://github.com/fabyr/cursor-imager-di.git
cd cursor-imager-di
virtualenv env
source env/bin/activate
python -m pip install -r requirements.txt

python gui.py
```

### Windows installation
Download this repository and extract it to a folder.
Open command prompt (cmd.exe) in that directory.
One way to do this is to press `Windows Key + R` and type `cmd.exe` and then OK.

To navigate to said folder type
```
C:
cd C:\Path\To\Extracted\Folder
```
(If on another drive other than `C`, use that drive letter instead)

Then, setup the environment as follows:
```
python -m venv env
env\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r windows_requirements.txt
```
Start the program using `python gui.py`.

For conveniance a batch file can be created to automatically start it without the
need to enter the virtual python environment manually every time:
```
call env\Scripts\activate
python gui.py
```

## Motivation
I am inherently bad at drawing with a mouse, so to impress some people
in VRChat I got the idea to develop this program.

I wanna apologize to anyone who actually thought i am a good artist.
But with a huge crowd around me it's hard to bring up an explanation >.<