import cv2
import numpy as np
from pydantic import BaseModel
from typing import Optional, List, Tuple

from .recognition_module import *
from .mask_structure import *

from camera_robot_tracing.mlModel import FindRoboNNetwork

from .find_coordinate import HomographyTranslate

"""JSON SCHEMA"""
#Dataclass about info center dotes
class DothCenter(BaseModel):
    name_doth: Optional[str]
    coordinate: Optional[Tuple]


class AllCoordinate(BaseModel):
    all_coordinate: List[DothCenter]


class GlobalCamera:
    all_coordinate: np.array
    new_cooordinate: np.array
    homog: HomographyTranslate

    NetworkRobot: FindRoboNNetwork
    real_coordinate = np.array
    status_homo = False

    def __init__(self, real_cr: np.array):
        self.RecSys = RecognitionUnit() #инцилизация камеры
        self.NetworkRobot = FindRoboNNetwork() #нейронной сети
        self.all_coordinate = np.array([])
        self.all_coordinate = np.vander(self.all_coordinate, 2)

        self.new_coordinate = np.array([])
        self.new_coordinate = np.vander(self.new_coordinate, 2)

        self.real_coordinate = real_cr

        if self.real_coordinate.shape[0] != 0:
            self.start_homograhy()

# mouse callback function

    def touch_window(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            if self.status_homo:
                real_cr = self.find_real_cr(np.array([x, y]))
                x = real_cr[0]
                y = real_cr[1]
            self.all_coordinate = np.append(self.all_coordinate, [[x, y]], axis=0)

            cv2.circle(self.img, (x, y), 50, (255, 0, 255), -1)
            print('Координаты x =: {0}, y =: {1}'.format(x, y))

    def start_homograhy(self):
        self.RecSys.open_camera()
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.touch_window)
        while True and self.all_coordinate.shape[0] < 4:

            self.img = self.RecSys.run()
            cv2.imshow('image', self.img)
            if cv2.waitKey(20) & 0xFF == 27:
                    break

        self.RecSys.close_camera()
        cv2.destroyAllWindows()

        self.homog = HomographyTranslate(self.real_coordinate, self.all_coordinate)
        self.homog.find_homo_array()
        self.status_homo = True

    def show_image(self):
        windowName = 'Image preview'
        while True:
            cv2.imshow(windowName, self.RecSys.get_image())
            if (cv2.waitKey(50) & 0xFF == ord('q')) or (cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1):
                break

    def find_real_cr(self, new_coordinate: np.array):
        rl_coordinate = self.homog.find_real_coordinate(new_coordinate)
        print(rl_coordinate)

        return np.array([int(rl_coordinate[0]), int(rl_coordinate[1])])

    def get_image(self):
        self.RecSys.open_camera()
        img = self.RecSys.run()
        self.RecSys.close_camera()

        return img

    def find_coordinate_robo(self, img=None):
        if img is None:
            data = self.NetworkRobot.get_bbox_from_tensor(self.get_image())
        else:
            data = self.NetworkRobot.get_bbox_from_tensor(img)

        if data is not None:
            try:
                np_cr = np.array([int(data[0]['point'][0]), int(data[0]['point'][1])])
                real_cr = self.find_real_cr(np_cr)

                print("I FIND COORDINATE ROBO ", real_cr)
                return real_cr
            except IndexError:
                return None
        else:
            print("I NOT FIND COORDINATE ROBO")
            return None

    def find_hit_robo(self, img):
        return self.NetworkRobot.get_frame_from_tensor(img)

    def show_traectory(self, old_points, robot_coords, target_point, img=None):
        if img is None:
            img = self.get_image()

        for i in range(len(old_points)):
            pix_cor_old = self.homog.find_pixel_coordinate(np.array([int(old_points[i][0]), int(old_points[i][1])]))
            cv2.circle(img, (int(pix_cor_old[0]), int(pix_cor_old[1])), 5, (0, 255, 0), -1)

        pix_cor_robot = self.homog.find_pixel_coordinate(np.array([int(robot_coords[0]), int(robot_coords[1])]))
        for one_target in target_point:
            if one_target.status is False:
                pix_cor_target = self.homog.find_pixel_coordinate(np.array([int(one_target.coordinate_rl[0]), int(one_target.coordinate_rl[1])]))
                cv2.line(img, (int(pix_cor_robot[0]), int(pix_cor_robot[1])), (int(pix_cor_target[0]), int(pix_cor_target[1])), (0, 0, 255), 2)
        return img

    def touch_real_cr(self, size_touch: int):
        if size_touch is not None and size_touch > 0:
            self.all_coordinate = np.array([])
            self.all_coordinate = np.vander(self.all_coordinate, 2)

            self.RecSys.open_camera()
            cv2.namedWindow('image')
            cv2.setMouseCallback('image', self.touch_window)
            while True and self.all_coordinate.shape[0] < size_touch:

                self.img = self.RecSys.run()
                cv2.imshow('image', self.img)
                if cv2.waitKey(20) & 0xFF == 27:
                        break

            self.RecSys.close_camera()
            cv2.destroyAllWindows()
            return self.all_coordinate
        else:
            return None


