from input import Input
import pyautogui
import pydirectinput

# This code is functional on windows, though terribly slow
class InputWindows(Input):
    def mouse_up(self) -> None:
        pydirectinput.mouseUp()
    def mouse_down(self) -> None:
        pydirectinput.mouseDown()
    def mouse_move_relative(self, dx : int, dy : int) -> None:
        pydirectinput.moveRel(dx, dy, relative=True)