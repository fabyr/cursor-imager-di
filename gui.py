from tkinter import *
from tkinter import filedialog

from cv2 import drawChessboardCorners

import core
import platform
import time

import bindglobal as bg

import asyncio
import threading

class CursorImagerGUI:
    def __init__(self) -> None:
        self.window = Tk()
        self.last_press = time.time()
        self.window.title("Cursor Imager")
        self.window.geometry("800x800")

        self.btnSelectImage = Button(self.window, text="Select Image", fg="black", command=self.button_select_image)
        self.btnSelectImage.grid()
        self.lblHotkey = Label(self.window, text="Hotkey: ")
        self.lblHotkey.grid()
        self.txtSetHotkey = Entry(self.window, text="<None>", fg="black")
        self.txtSetHotkey.bind("<Key>", self.txt_hotkey_type)
        self.txtSetHotkey.grid()
        self.btnReset = Button(self.window, text="Reset Drawing Progress", fg="black", command=self.button_reset)
        self.btnReset.grid()
        
        self.input = None
        pf = platform.system()
        if pf == "Linux":
            import input_linux
            self.input = input_linux.InputLinux()
        elif platform.system() == "Windows":
            import input_windows
            self.input = input_windows.InputWindows()
        else:
            raise Exception("Unsupported Platform")
        self.params = core.DrawingParameters()
        self.params.default()
        self.drawing_machine = core.DrawingMachine(self.input, self.params)

    def button_select_image(self):
        filetypes = [
            ("Portable Network Graphics", "*.png"),
            ("Joint Photographics Expert Group", "*.jpg")
        ]
        filename = filedialog.askopenfilename(title="Open Image", filetypes=filetypes)
        if filename:
            self.drawing_machine.image_init(filename)
    
    def txt_hotkey_type(self, e):
        print(f"Bind Hotkey: {e.char}")
        new_hotkey = e.char

        if self.current_hotkey:
            self.bg.gunbind(self.current_hotkey, self.hotkey_callback)
        
        self.bg.gbind(new_hotkey, self.hotkey_callback)
        self.current_hotkey = new_hotkey
        
        self.txtSetHotkey.delete(0, END)

    def button_reset(self):
        self.drawing_machine.reset()

    def hotkey_callback(self, e):
        print("Hotkey: %s" % e)
        now = time.time()
        if now - self.last_press < 0.1:
            return
        self.last_press = now
        if self.drawing_machine.exit:
            if self.drawing_machine.image is not None:
                _thread = threading.Thread(target=asyncio.run, args=(self.drawing_machine.thread_loop(),))
                _thread.start()
        else:
            self.drawing_machine.active = not self.drawing_machine.active

    def main(self):
        self.current_hotkey = None
        self.bg = bg.BindGlobal()
        self.bg.start()
        self.window.mainloop()
        

if __name__=="__main__":
    CursorImagerGUI().main()