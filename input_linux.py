from input import Input
import os

class InputLinux(Input):
    def mouse_up(self) -> None:
        os.system("xdotool mouseup 1") # 1 is for left button
    def mouse_down(self) -> None:
        os.system("xdotool mousedown 1") # 1 is for left button
    def mouse_move_relative(self, dx : int, dy : int) -> None:
        # the "--" is needed to allow negative numbers
        os.system(f"xdotool mousemove_relative -- {dx} {dy}")