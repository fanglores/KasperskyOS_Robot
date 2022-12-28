import numpy as np
import cv2

MIN_AREA = 1000
MAX_AREA = 2000

class Point:
    def __init__(self, ar, co, xc, yc):
        self.area = ar
        self.contour = co
        self.x = xc
        self.y = yc


class Markers:
    def __init__(self, tp, cc, lb, ub):
        self.color_name = tp
        self.color = cc

        self.mask = {'lower': lb, 'upper': ub}

        self.points = []

    def set_contour(self, contours):
        self.points = []

        for c in contours:  # for every found contour
            if c is not None:  # check if it`s not empty
                M = cv2.moments(c)
                if M["m00"] > MIN_AREA and M["m00"] < MAX_AREA:  # find the contour which area > const size
                    self.points.append(Point(M["m00"], c, int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])))


ColorsDict = [
    Markers('red', (0, 0, 255), np.array([0, 200, 160], np.uint8), np.array([180, 255, 255], np.uint8)),
    Markers('green', (0, 255, 0), np.array([25, 52, 72], np.uint8), np.array([102, 255, 255], np.uint8)),
    Markers('blue', (255, 0, 0), np.array([94, 80, 2], np.uint8), np.array([120, 255, 255], np.uint8))
]
