from tkinter import *
from tkinter import filedialog
from xmlrpc.client import MAXINT

from PIL import ImageTk, Image

import core
import platform
import time

import bindglobal as bg

import asyncio
import threading

class CursorImagerGUI:
    def numberValidation(self, s) -> None:
        if s in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return True
        self.window.bell() # bell() plays sound to signal wrong input
        return False

    def __init__(self) -> None:
        self.window = Tk()
        self.last_press = time.time()
        self.window.title("Cursor Imager")
        self.window.geometry("800x800")

        #################
        ### GUI Setup ###
        #################
        self.window.columnconfigure(1, weight=0)
        self.window.configure(padx=30, pady=30)

        self.btnSelectImage = Button(self.window, text="Select Image", fg="black", command=self.button_select_image)
        self.btnSelectImage.grid(sticky="WE")
        self.lblHotkey = Label(self.window, text="Hotkey: ")
        self.lblHotkey.grid(sticky="N")
        self.txtSetHotkey = Entry(self.window, text="<None>", fg="black")
        self.txtSetHotkey.bind("<Key>", self.txt_hotkey_type)
        self.txtSetHotkey.grid(sticky="N")
        self.btnReset = Button(self.window, text="Reset Drawing Progress", fg="black", command=self.button_reset)
        self.btnReset.grid(sticky="WE")

        self.lblSpeedInfo = Label(self.window, text="Drawing Speed: ")
        self.lblSpeedInfo.grid(sticky="N", pady=(15, 0))
        self.scaleSpeedValue = DoubleVar()
        self.scaleSpeed = Scale(self.window, from_=1, to=20, orient='horizontal', variable=self.scaleSpeedValue, command=self.scale_speed_slide)
        self.scaleSpeed.grid(sticky="WE")

        self.lblScaleInfo = Label(self.window, text="Drawing Scale: ")
        self.lblScaleInfo.grid(sticky="N")
        self.scaleScaleValue = DoubleVar()
        self.scaleScale = Scale(self.window, from_=1, to=10, orient='horizontal', variable=self.scaleScaleValue, command=self.scale_scale_slide)
        self.scaleScale.grid(sticky="WE", pady=(0, 15))
        
        self.cbDoEdgeValue = BooleanVar()
        self.cbDoEdge = Checkbutton(self.window, text="Edge detection", variable=self.cbDoEdgeValue, onvalue=True, offvalue=False, command=self.cbDoEdge_press)
        self.cbDoEdge.grid(sticky="NW")

        self.cbInvertValue = BooleanVar()
        self.cbInvert = Checkbutton(self.window, text="Invert", variable=self.cbInvertValue, onvalue=True, offvalue=False, command=self.cbInvert_press)
        self.cbInvert.grid(sticky="NW")

        self.lblMaxApartInfo = Label(self.window, text="Max Path Combine Distance: ")
        self.lblMaxApartInfo.grid(sticky="N")
        
        vcmd = (self.window.register(self.numberValidation), '%S')

        self.txtMaxApartValue = StringVar()
        self.txtMaxApart = Entry(self.window, validate="key", vcmd=vcmd, textvariable=self.txtMaxApartValue)
        self.txtMaxApart.bind("<KeyRelease>", self.txt_max_apart)
        self.txtMaxApart.grid(sticky="WE")
        self.txtMaxApartValue.set("3")

        self.lblMaxContinousInfo = Label(self.window, text="Max Continous Path: ")
        self.lblMaxContinousInfo.grid(sticky="N")
        
        self.txtMaxContinousValue = StringVar()
        self.txtMaxContinous = Entry(self.window, validate="key", vcmd=vcmd, textvariable=self.txtMaxContinousValue)
        self.txtMaxContinous.bind("<KeyRelease>", self.txt_max_continous)
        self.txtMaxContinous.grid(sticky="WE")
        self.txtMaxContinousValue.set("1000")

        self.btnRecalc = Button(self.window, text="(Re)Calculate Image", fg="black", command=self.recalc_image)
        self.btnRecalc.grid(sticky="WE")

        self.lblInfo = Label(self.window, text="Preview image (White pixels will be drawn)")
        self.lblInfo.grid(sticky="NW", row=0, column=1, padx=20)

        self.imgDisplay = Label(self.window, borderwidth=1, relief="solid")
        self.imgDisplay.grid(sticky="NW", row=1, rowspan=16, column=1, padx=20, pady=20)

        self.lblInitialText = "Not drawing."
        self.lblDrawingText = "Drawing in progress..."
        self.lblDrawingStatus = Label(self.window, text=self.lblInitialText)
        self.lblDrawingStatus.grid(sticky="N", padx=20, pady=20)
        
        self.lblDrawingPercentage = Label(self.window, text="0.0% Done")
        self.lblDrawingPercentage.grid(sticky="N", padx=20, pady=20)

        self.input = None
        pf = platform.system()

        # use different mouse-input-manager depending on the OS
        if pf == "Linux":
            import input_linux
            self.input = input_linux.InputLinux()
        elif platform.system() == "Windows":
            import input_windows
            self.input = input_windows.InputWindows()
        else:
            raise Exception("Unsupported Platform")

        # initialize core drawing functionality
        self.params = core.DrawingParameters()
        self.params.default()

        # call all callbacks once to ensure the params are in their default state 
        # and coherent with the GUI
        self.scale_speed_slide(None)
        self.scale_scale_slide(None)
        self.cbDoEdge_press()
        self.cbInvert_press()
        self.txt_max_apart(None)
        self.txt_max_continous(None)

        self.drawing_machine = core.DrawingMachine(self.input, self.params)
        self.drawing_machine.done_callback = lambda: self.lblDrawingStatus.configure(text="Done drawing!")
        self.drawing_machine.percentage_callback = lambda x: self.lblDrawingPercentage.configure(text="%.1f%% Done" % (x * 100))
        self.drawing_machine.active_change_callback = lambda: \
                self.lblDrawingStatus.configure(text=self.lblDrawingText if self.drawing_machine.active else self.lblInitialText)

    def button_select_image(self):
        filetypes = [
            ("Portable Network Graphics", "*.png"),
            ("Joint Photographics Expert Group", "*.jpg")
        ]
        filename = filedialog.askopenfilename(title="Open Image", filetypes=filetypes)
        if filename:
            self.drawing_machine.image_filename = filename
            #self.drawing_machine.image_init(filename)
    
    def recalc_image(self):
        if self.drawing_machine.image_filename:
            self.drawing_machine.image_init(self.drawing_machine.image_filename)
            global img
            img = self.drawing_machine.preview()
            img = ImageTk.PhotoImage(Image.fromarray(img).convert('RGB'))
            self.imgDisplay.configure(image=img)
    
    def txt_hotkey_type(self, e):
        self.txtSetHotkey.delete(0, END)
        print(f"Bind Hotkey: {e.char}")
        
        new_hotkey = e.char

        if self.current_hotkey:
            self.bg.gunbind(self.current_hotkey, self.hotkey_callback)
        
        self.bg.gbind(new_hotkey, self.hotkey_callback)
        self.current_hotkey = new_hotkey

    def button_reset(self):
        self.drawing_machine.reset()

    def scale_speed_slide(self, e):
        self.params.sleep_between_action = 1.0 / self.scaleSpeedValue.get() * 0.02;

    def scale_scale_slide(self, e):
        self.params.scale = int(self.scaleScaleValue.get());

    def cbDoEdge_press(self):
        self.params.do_edge = self.cbDoEdgeValue.get()
    
    def cbInvert_press(self):
        self.params.invert = self.cbInvertValue.get()

    def txt_max_apart(self, e):
        str = self.txtMaxApartValue.get()
        self.params.path_max_apart = 0 if not str else int(str)
    
    def txt_max_continous(self, e):
        str = self.txtMaxContinousValue.get()
        self.params.max_continous_line = 0 if not str else int(str)

    def hotkey_callback(self, e):
        print("Hotkey: %s" % e)
        now = time.time()
        if now - self.last_press < 0.1: # small "debounce" delay
            return
        self.last_press = now

        # if a drawing process was not started yet, start it
        if self.drawing_machine.exit:
            if self.drawing_machine.image is not None:
                _thread = threading.Thread(target=asyncio.run, args=(self.drawing_machine.thread_loop(),))
                _thread.start()
        else: # if already drawing, toggle pause
            self.drawing_machine.active = not self.drawing_machine.active
            self.drawing_machine.active_change()

    def main(self):
        self.current_hotkey = None
        self.bg = bg.BindGlobal() # Global hotkeys
        self.bg.start()
        self.window.mainloop()
        

if __name__=="__main__":
    CursorImagerGUI().main()