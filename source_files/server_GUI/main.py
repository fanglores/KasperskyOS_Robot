from camera_robot_tracing.main_find_sticker import GlobalCamera
from logic_drive.logic_drive import Robot
from logic_drive.logic_drive import Target
from connect_robot.connect_robo import find_my_ip

import numpy as np


class WorkedSystem:
    real_coordinate = np.array([[0, 0],
                                [58, 0],
                                [0, 108],
                                [58, 108]]) #for create matrix homografy


    type_drive = 'dot' #  color or dot

    touch_stack_coordinate: Target
    IPCONFIG = '127.0.0.1'

    def __init__(self):
        self.IPCONFIG = find_my_ip(self.IPCONFIG)
        print("MY IP", self.IPCONFIG)

        self.camera = GlobalCamera(self.real_coordinate)
        self.robot = Robot(self.camera, self.IPCONFIG)
        self.touch_stack_coordinate = Target(self.camera, 2)

    def new_stack_target_color(self):
        while self.type_drive == 'color' and self.touch_stack_coordinate.get_size_target() > 0:
            new_cor_tar = self.robot.find_new_target(self.touch_stack_coordinate)
            self.robot.start_new_target(new_cor_tar)

    def start_touch_target(self):
        while self.type_drive == 'dot':
            while self.touch_stack_coordinate.get_size_target() > 0 and self.type_drive == 'dot':
                new_tar = self.robot.find_new_target(self.touch_stack_coordinate)
                self.robot.start_new_target(new_tar)

    def add_new_touch(self, coordinate: np.array):
        self.touch_stack_coordinate.add_coordinate(coordinate)

