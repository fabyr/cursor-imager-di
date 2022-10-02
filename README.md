# cursor-imager-di

A tool to draw images using your mouse!
Compatible with both Windows and Linux.
On Windows DirectInput is used and on Linux xdotool must be installed,
which even makes it work in most games!

## Functionality and how it works
Any generic image can be loaded, to which, if desired, edge detection is performed, so only lines and not regions are drawn.
After that a path finding algorithm finds a connected path throughout the entire image.
(Or multiple connected paths).
Then with the press of a selectable hotkey your mouse will be controlled according to the processed image, and will hopefully draw something resembling the input image.

After starting the python script you'll be greeted with a Graphical Interace
allowing you to change some settings.
Those include things such as:
- Automatic Edge detection?
- Speed of cursor movement
- Parameters for controlling the Path-Finding-Algorithm
- ...

## Installation
This program works both on Windows and Linux.
Python 3 is required to be installed on your system. (Tested with Python 3.8.10)

[Python Download](https://www.python.org/downloads/)

### Linux installation
(Tested on Linux Mint 20.2)
Required to be installed on the system: xdotool (`sudo apt install xdotool`)

```
git clone https://github.com/fabyr/cursor-imager-di.git
cd cursor-imager-di-main
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
cd Path\To\Extracted\Folder
```

Then, setup the environment as follows:
```
python -m venv env
env\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r windows_requirements.txt

python gui.py
```

## Motivation
I am inherently bad at drawing with a mouse, so to impress some people
in VRChat I got the idea to develop this program.

I wanna apologize to anyone who actually thought i am a good artist.
But with a huge crowd around me it's hard to bring up an explanation >.<