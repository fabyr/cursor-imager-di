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
    edge_threshold1: int
    edge_threshold2: int
    scale: int
    min_path_length: int
    ridge_max_apart: int
    sleep_between_action: float
    max_continous_line: int

    def default(self):
        self.do_edge = True
        self.edge_threshold1 = 30
        self.edge_threshold2 = 120
        self.scale = 1
        self.min_path_length = 2
        self.ridge_max_apart = 3
        self.sleep_between_action = 0.001
        self.max_continous_line = 500

class DrawingMachine:
    def __init__(self, input : Input, params : DrawingParameters) -> None:
        self.input = input
        self.parameters = params
        self.point_idx = 0
        self.contour_idx = 0
        self.drawn_points = 0
        self.offset = None
        self.image = None
        self.raw_contours = None
        self.contours = None
        self.contour = None
        self.active = False
        self.exit = True
    
    def image_init(self, filename : str) -> None:
        image = cv2.imread(filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if self.parameters.do_edge:
            image = cv2.Canny(image, threshold1=self.parameters.edge_threshold1, \
                                threshold2=self.parameters.edge_threshold2)
        self.raw_contours = ridge_simple(image, self.parameters.ridge_max_apart)
        self.image = image

        processed = []

        for contour in self.raw_contours:
            if len(contour) > self.parameters.min_path_length:
                processed.append(contour)
        self.contours = processed

        self.offset = processed[0][0] # the first point determines the offset
        self.reset()

    def fetch_contour(self) -> None:
        if self.contour_idx < len(self.contours):
            self.contour = self.contours[self.contour_idx]

    def reset(self) -> None:
        self.exit = True
        self.point_idx = 0
        self.contour_idx = 0
        self.drawn_points = 0
        self.fetch_contour()

    def step(self) -> None:
        if self.point_idx == 0:
            self.input.mouse_down()
            pause()
        self.drawn_points += 1
        if self.parameters.max_continous_line != 0 and self.drawn_points % self.parameters.max_continous_line == 0:
            self.input.mouse_up()
            pause()
            self.input.mouse_down()
            pause()
            
        yLast, xLast = (0, 0)
        x, y = (0, 0)
        if self.point_idx > 0:
            xLast, yLast = self.contour[self.point_idx - 1]
            xLast, yLast = (xLast - self.offset[0], yLast - self.offset[1])
            x, y = self.contour[self.point_idx]
            x, y = (x - self.offset[0], y - self.offset[1])
            yDiff, xDiff = (y - yLast, x - xLast)
            yDiff, xDiff = (yDiff * self.parameters.scale, xDiff * self.parameters.scale)

            self.input.mouse_move_relative(int(xDiff), int(yDiff))
            
        self.point_idx += 1
        if self.point_idx >= len(self.contour):
            self.point_idx = 0
            self.contour_idx += 1
            self.fetch_contour()

            if self.contour_idx >= len(self.contours):
                self.active = False
                self.reset()
                print("Done.")
                self.input.mouse_up()
                pause()
            else:
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
    
    async def thread_loop(self) -> None:
        self.active = True
        self.exit = False
        while not self.exit:
            if self.active:
                self.step()
            pause(self.parameters.sleep_between_action)
        self.active = False

def single_ridge(image : np.ndarray, visited : np.ndarray, x: int, y: int, max_distance : int) -> list:
	ridge = []
	w = image.shape[0]
	h = image.shape[1]
	get = lambda xx, yy: xx >= 0 and xx < w and yy >= 0 and yy < h and visited[xx, yy] == 0 and image[xx, yy] == 255
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
	w = image.shape[0]
	h = image.shape[1]
	visited = np.zeros_like(image)
	ridges = []
	for y in range(h):
		for x in range(w):
			if visited[x, y] == 0 and image[x, y] == 255:
				ridge = single_ridge(image, visited, x, y, max_ridge_distance)
				ridges.append(ridge)
	return ridges