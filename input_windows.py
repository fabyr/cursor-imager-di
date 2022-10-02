from input import Input
import pyautogui
import pydirectinput

# TODO: This code is not yet checked if functional on windows
class InputWindows(Input):
    def mouse_up(self) -> None:
        pydirectinput.mouseUp()
    def mouse_down(self) -> None:
        pydirectinput.mouseDown()
    def mouse_move_relative(self, dx : int, dy : int) -> None:
        pydirectinput.moveRel(dx, dy, relative=True)