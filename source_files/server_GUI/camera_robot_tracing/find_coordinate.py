import numpy as np
import cv2

from pydantic import BaseModel
from typing import Optional, List, Tuple

#Dataclass about info center dotes
class DothCenter(BaseModel):
    name_doth: Optional[str]
    coordinate: Optional[Tuple]


class HomographyTranslate:
    H_array: np.array
    back_H_array: np.array
    real_cr: np.array #реальное расстояние от камеры
    pixel_cr: np.array #расположение на камере от камеры

    def __init__(self, real_cr: np.array, pixel_cr: np.array):
        self.real_cr = real_cr
        self.pixel_cr = pixel_cr

    def find_homo_array(self):
        self.H_array, status = cv2.findHomography(self.pixel_cr, self.real_cr)
        self.back_H_array, status2 = cv2.findHomography(self.real_cr, self.pixel_cr)

    def find_real_coordinate(self, new_coordinate):
        if self.H_array.shape[0] > 0 and self.H_array.shape[1] > 0:
            add_new_coordinate = np.array([new_coordinate[0], new_coordinate[1], 1])
            res = np.dot(self.H_array, add_new_coordinate)

            return res / res[2]

    def find_pixel_coordinate(self, new_coordinate):
        if self.back_H_array.shape[0] > 0 and self.back_H_array.shape[1] > 0:

            add_new_coordinate = np.array([new_coordinate[0], new_coordinate[1], 1])
            res = np.dot(self.back_H_array, add_new_coordinate)
            return res / res[2]





