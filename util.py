import math

def distance(x1 : float, y1 : float, x2 : float, y2 : float):
	xdiff = x2 - x1
	ydiff = y2 - y1
	return math.sqrt(xdiff * xdiff + ydiff * ydiff)