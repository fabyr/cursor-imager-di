from input import Input
import pyautogui
import pydirectinput

class InputWindows(Input):
    direct: bool = False

    def __init__(self) -> None:
        super().__init__()
        pyautogui.PAUSE = 0
        pydirectinput.PAUSE = 0

    def mouse_up(self) -> None:
        if self.direct:
            pydirectinput.mouseUp()
        else:
            pyautogui.mouseUp()
    def mouse_down(self) -> None:
        if self.direct:
            pydirectinput.mouseDown()
        else:
            pyautogui.mouseDown()
    def mouse_move_relative(self, dx : int, dy : int) -> None:
        if self.direct:
            pydirectinput.moveRel(dx, dy)
        else:
            pyautogui.moveRel(dx, dy)
