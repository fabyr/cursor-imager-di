from input import Input
import numpy as np
import cv2
import time

action_delay = 0.1

# this is its own function to easily change the method of sleeping if done so in the future
def pause(x : float = action_delay) -> None:
    time.sleep(x)

class DrawingParameters:
    do_edge: bool
    invert: bool
    edge_threshold1: int
    edge_threshold2: int
    scale: int
    min_path_length: int
    path_max_apart: int
    sleep_between_action: float
    max_continous_line: int

    def default(self):
        self.do_edge = True
        self.edge_threshold1 = 30
        self.edge_threshold2 = 120
        self.scale = 1
        self.min_path_length = 2
        self.path_max_apart = 3
        self.sleep_between_action = 0.001
        self.max_continous_line = 500

class DrawingMachine:
    def __init__(self, input : Input, params : DrawingParameters) -> None:
        self.input = input
        self.parameters = params
        self.point_idx = 0
        self.contour_idx = 0
        self.drawn_points = 0
        self.total_points = 0
        self.previous_percentage = 0.0
        self.offset = None
        self.image = None
        self.image_filename = None
        self.raw_contours = None
        self.contours = None
        self.contour = None
        self.active = False
        self.exit = True
        self.active_change_callback = None
        self.done_callback = None
        self.percentage_callback = None
    
    def image_init(self, filename : str) -> None:
        """
        Calling this method will replace the old image (if any) with a new image
        and will perform all necessary calculations to prepare for drawing.
        """
        self.image_filename = filename
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


        if self.parameters.invert:
            image = 255-image # will subtract all channels from 255

        if self.parameters.do_edge:
            image = cv2.Canny(image, threshold1=self.parameters.edge_threshold1, \
                                threshold2=self.parameters.edge_threshold2)
        
        self.raw_contours = ridge_simple(image, self.parameters.path_max_apart)
        self.image = image

        processed = []

        self.total_points = 0
        # filter out any contours which are too short
        for contour in self.raw_contours:
            if len(contour) > self.parameters.min_path_length:
                processed.append(contour)
                self.total_points += len(contour)
        self.contours = processed

        self.offset = processed[0][0] # the first point determines the offset
        self.reset()

    def fetch_contour(self) -> None:
        """
        Update self.contour according to the current index (self.contour_idx)
        """
        if self.contour_idx < len(self.contours):
            self.contour = self.contours[self.contour_idx]

    def reset(self) -> None:
        """
        Reset to the initial state
        """
        self.exit = True
        self.point_idx = 0
        self.contour_idx = 0
        self.drawn_points = 0
        self.previous_percentage = 0
        self.percentage_change(0)
        self.fetch_contour()

    def preview(self, scale : int = None) -> np.ndarray:
        """
        Generates a preview image of what the final result will look like
        If scale is supplied with None, the value will be taken from the supplied
        DrawingParameters
        """
        maxx, maxy = (0, 0)
        minx, miny = (65535, 65535)
        if not scale:
            scale = self.parameters.scale
        # find required dimensions for the output image (min and max search for the point-extrema)
        for contour in self.contours:
            y, x = np.max(contour, axis=0)
            ym, xm = np.min(contour, axis=0)
            if x > maxx:
                maxx = x
            if xm < minx:
                minx = xm
            if y > maxy:
                maxy = y
            if ym < miny:
                miny = ym
        maxx, maxy = ((maxx) * scale, (maxy) * scale)
        minx, miny = ((minx) * scale, (miny) * scale)

        # make a black image
        image = np.zeros((int(maxx-minx), int(maxy-miny), 3), np.uint8)
        
        # draw all contours
        for contour in self.contours:
            lx, ly = (None, None)
            for idx in range(len(contour)):
                y, x = contour[idx]
                if lx is not None and ly is not None:
                    cv2.line(image, (int((ly) * scale - miny), int((lx) * scale - minx)), (int((y) * scale - miny), int((x) * scale - minx)), (255, 255, 255), 1)
                lx, ly = x, y
        return image

    def step(self) -> None:
        """
        Performs one single mouse operation of the drawing sequence.
        Automatically rolls over to the next contour if the current one is exhausted.
        """
        if self.point_idx == 0:
            self.input.mouse_down()
            pause()
        self.drawn_points += 1
        self.percentage_change(self.drawn_points / self.total_points)
        if self.parameters.max_continous_line != 0 and self.drawn_points % self.parameters.max_continous_line == 0:
            self.input.mouse_up()
            pause()
            self.input.mouse_down()
            pause()
            
        yLast, xLast = (0, 0)
        x, y = (0, 0)
        if self.point_idx > 0: # if we are at the second point of the contour or more, we can draw a line between the last one and the current one
            xLast, yLast = self.contour[self.point_idx - 1]
            xLast, yLast = (xLast - self.offset[0], yLast - self.offset[1])
            x, y = self.contour[self.point_idx]
            x, y = (x - self.offset[0], y - self.offset[1])
            yDiff, xDiff = (y - yLast, x - xLast)
            yDiff, xDiff = (yDiff * self.parameters.scale, xDiff * self.parameters.scale)

            # the mouse is in down-state all the time, so this creates a line between the current mouse position and the next one
            self.input.mouse_move_relative(int(xDiff), int(yDiff))
            
        self.point_idx += 1
        if self.point_idx >= len(self.contour): # the current contour is finished
            self.point_idx = 0
            self.contour_idx += 1
            self.fetch_contour()

            if self.contour_idx >= len(self.contours): # all contours are finished
                self.active = False
                self.reset()
                self.input.mouse_up()
                pause()
            else: # if not all contours are finished, we can do some preparations to go to the starting location of the next contour
                x2, y2 = self.contour[self.point_idx]
                x2, y2 = (x2 - self.offset[0], y2 - self.offset[1])
                
                xDiff = int((x2 - x) * self.parameters.scale)
                yDiff = int((y2 - y) * self.parameters.scale)
                self.input.mouse_up()
                pause()
                self.input.mouse_move_relative(xDiff, yDiff)
                pause()
                self.input.mouse_down()
                pause()
    
    # some crude callback-triggering methods
    # intended to only be run from inside this class
    def active_change(self) -> None:
        if self.active_change_callback:
            self.active_change_callback()

    def done_change(self) -> None:
        if self.done_callback:
            self.done_callback()

    def percentage_change(self, x) -> None:
        # only update if a text change is visible, i.e. changed more than 0.1% since the last update
        if abs(self.previous_percentage - x) >= 0.001:
            self.previous_percentage = x
            if self.percentage_callback:
                self.percentage_callback(x)
                
    def thread_loop(self) -> None:
        """
        Continually calls step in fixed time intervals (DrawingParameters.sleep_between_action).
        Terminates once all contours are finished
        """
        self.active = True
        self.active_change()
        self.exit = False
        while not self.exit:
            if self.active:
                self.step()
            pause(self.parameters.sleep_between_action)
        self.active = False
        self.active_change()
        self.done_change()
        print("Done drawing.")

# i am a novice at numpy
# this could probably be sped up by a lot if it would make use of some numpy functions
def single_ridge(image : np.ndarray, visited : np.ndarray, x: int, y: int, max_distance : int) -> list:
    """
    Traverses the image starting from the supplied x and y coordinates and
    records a single pixel wide path until no bright pixels can be found anymore in close proximity.
    (governed by max_distance)
    """
    ridge = []
    w = image.shape[0]
    h = image.shape[1]

    # returns a boolean value
    # True only if the pixel has not been visited before and only if that pixes is "bright" (value greater than 127)
    get = lambda xx, yy: xx >= 0 and xx < w and yy >= 0 and yy < h and visited[xx, yy] == 0 and image[xx, yy] > 127
    
    # base scanning offsets
    # no matter the distance, first all 8 pixels around the current ones will be checked
    mat1 = \
    [
        [0, -1],
        [-1,  0], [1,  0],
        [0,  1],
    ]
    mat2 = \
    [
        [-1, -1],  [1, -1],
        [-1,  1], [1,  1]
    ]

    mats = [mat1, mat2]
    while True:
        found = False
        ridge.append([y, x])
        visited[x, y] = 1
        
        # check both offset lists
        for mat in mats:
            for elem in mat:
                dx, dy = elem
                if get(x + dx, y + dy):
                    x += dx
                    y += dy
                    found = True
                    break
            if found:
                break
        
        # if not yet found in the single ring around the pixel
        # use a more generic approach
        # -> Spiral outwards until a pixel is found or until the distance is above max_distance
        # at which point no pixel is found
        if not found:
            order = 2
            dcounter = 0
            counter = 0
            dxx = [1, 0, -1, 0]
            dyy = [0, 1, 0, -1]
            dxv, dyv = (-order, -order)
            while order < max_distance:
                if get(x + dxv, y + dyv):
                    x += dxv
                    y += dyv
                    found = True
                    break
                dxv, dyv = (dxv + dxx[counter], dyv + dyy[counter])
                dcounter += 1
                if dcounter >= order * 2 + 1:
                    dcounter = 0
                    counter += 1
                    if counter > 3:
                        counter = 0
                        order += 1
                        dxv, dyv = (-order, -order)
        if not found:
            break
    return ridge

def ridge_simple(image : np.ndarray, max_ridge_distance : int) -> list:
    """
    Continously Calls single_rigde() until all pixels in the image have been visited and
    are part of a path.
    Returns a list of all the paths
    """
    w = image.shape[0]
    h = image.shape[1]
    visited = np.zeros_like(image)
    ridges = []
    for y in range(h):
        for x in range(w):
            if visited[x, y] == 0 and image[x, y] > 127:
                ridge = single_ridge(image, visited, x, y, max_ridge_distance)
                ridges.append(ridge)
    return ridges