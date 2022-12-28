import cv2
import numpy as np

from .mask_structure import *

class RecognitionUnit:

    def __init__(self):
        pass

    def __del__(self):
        self.Camera.release()
        cv2.destroyAllWindows()

    def open_camera(self):
        self.Camera = cv2.VideoCapture(2)
        self.Camera.set(cv2.CAP_PROP_BUFFERSIZE, 0)

        self.Camera.set(3, 640)
        self.Camera.set(4, 480)

    def close_camera(self):
        self.Camera.release()


    def run(self):
        image = self.get_image()
        return image

    def color_run(self):
        image = self.get_image()
        self.update_contours(image)
        return image

    def get_image(self):
        try:
            ret, frame = self.Camera.read()
            if ret:
                return frame
            else:
                raise 'Retrieving error'
        except:
            print('[ERROR] Error while retrieving an image!')

    def update_contours(self, frame):
        hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        for color in ColorsDict:
            mask = cv2.inRange(hsvFrame, color.mask['lower'], color.mask['upper'])

            ret, gray_threshed = cv2.threshold(mask, 120, 200, cv2.THRESH_BINARY)  # Threshold grayscaled image to get binary image
            bilateral_filtered_image = cv2.bilateralFilter(gray_threshed, 5, 175, 175)  # Smooth an image
            edge_filtered_mask = cv2.Canny(bilateral_filtered_image, 75, 200)
            #
            kernel = np.ones((5, 5), np.float32) / 25
            filtered_mask = cv2.filter2D(edge_filtered_mask, -1, kernel)

            # find contours
            color.set_contour(cv2.findContours(filtered_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0])
