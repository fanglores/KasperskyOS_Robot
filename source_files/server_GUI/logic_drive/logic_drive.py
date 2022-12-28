from logic_drive.create_command import EngineCommandSchema
from logic_drive.coordinates_stack import CoordinatesStack
from logic_drive.calman_drive import KalmanFilter
from camera_robot_tracing.main_find_sticker import GlobalCamera

from logic_drive.angle_search import search
from logic_drive.create_command import Commands

import cv2
#from camera_robot_tracing.mlModel import get_bbox_from_tensor
from connect_robot.connect_robo import send_command

from time import sleep

from scipy.spatial.distance import cdist
from scipy.spatial.transform import Rotation
import numpy as np


class OneTarget:
    status: bool = False
    coordinate_rl: np.array

    def __init__(self, new_coordinate):
        self.coordinate_rl = new_coordinate

    def change_status(self):
        self.status = True


class Target:
    dev_coordinate: CoordinatesStack
    class_cor: list

    def __init__(self, camera: GlobalCamera = None, size=None, coordinate: np.array = None):
        self.class_cor = []

        if camera is not None:
            res = camera.touch_real_cr(size)
            if res is not None:
                self.dev_coordinate = CoordinatesStack(res)

            for one_doth in res:
                self.class_cor.append(OneTarget(one_doth))

        elif coordinate is not None:
            for one_doth in coordinate:
                self.class_cor.append(OneTarget(one_doth))
        else:
            print("ERROR GET COORDINATE")

    def get_size_target(self):
        try:
            return self.dev_coordinate.new_coordinate.shape[0]
        except:
            return 0

    def get_new_target(self, my_coordinate: np.array):
        print(self.dev_coordinate.new_coordinate)
        fun_min = cdist(my_coordinate[None], self.dev_coordinate.new_coordinate, metric="euclidean")
        index_min = np.nanargmin(fun_min)

        return self.dev_coordinate.new_coordinate[index_min], index_min

    def delete_last_coordinate(self):
        if self.dev_coordinate.new_coordinate.shape[0] > 0:
            self.dev_coordinate.new_coordinate = np.delete(self.dev_coordinate.new_coordinate, -1)

    def add_coordinate(self, coordinate):
        self.dev_coordinate.add_new_coordinates(coordinate)

    def all_status(self):
        for one_doth in self.class_cor:
            if one_doth.status is False:
                return True
        return False


"""     ROBOT     """


class Robot:
    my_commands: Commands
    my_coordinate: CoordinatesStack
    camera: GlobalCamera

    my_vector: np.array
    vector_target: np.array
    my_target_coordinate: np.array = None
    modul_distance_target: float = None

    line_speed: float = 45  # meters per second
    circular_speed: float = 45  # degrees per second

    error_rate: float = 0.1 # meters
    error_angle: float = 1

    ITER_FIND_TARGET_MAX: int = 50 #количесво итерационных движений
    ITER_FIND_TARGET_MIN: int = 5 #количесво итерационных движений

    def __init__(self, camera: GlobalCamera, IP_CONFIG):
        self.camera = camera
        self.my_coordinate = CoordinatesStack()
        self.my_commands = Commands()
        self.IP_CONFIG = IP_CONFIG

        self._find_my_coordinate()
        self.send_command_robot('tank', 1)

        input(("\nGO TO NEXT"))
        self._find_my_coordinate()

        self._find_my_vector()

    def _find_my_coordinate(self):
        """поиск координат робота"""
        while True:
            detect_robo = self.camera.find_coordinate_robo()
            if detect_robo is not [] or detect_robo is not None:
                try:
                    self.my_coordinate.add_new_coordinates(detect_robo)
                    print("[SYSTEM LOGIC] ~ FIND ROBO COORDINATE", detect_robo)
                    return detect_robo
                except TypeError:
                    continue

            else:
                print("[SYSTEM LOGIC] ~ NOT FIND ROBO COORDINATE")
                continue

    def _find_my_vector(self):
        """поиск вектора направления робота"""
        #print("ALL COORDINATE", self.my_coordinate.new_coordinate)
        self.my_vector = self.my_coordinate.new_coordinate[-1] - self.my_coordinate.new_coordinate[-2]
        print("[SYSTEM LOGIC] ~ FIND VECTOR ROBO ~ ", self.my_vector)

    def find_new_target(self, target: Target):
        new_tar = target.get_new_target(self.my_coordinate.get_last_coordinate())
        print("[SYSTEM LOGIC] ~ I AM FIND NEW TARGET", new_tar)
        return new_tar[0]

    def _path_traveled(self, first_c: np.array, second_c: np.array):
        """Поиск пройденного пути"""
        ph_traveled = cdist(first_c[None], second_c[None], metric="euclidean")[0]
        print("[SYSTEM LOGIC] I AM PATH TRAVELED", ph_traveled)
        return ph_traveled

    def send_command_robot(self, type_engine, time, speed=1):
        """ Формирование и отправка команд роботу"""
        new_commands = self.my_commands.add_new_command(type_command=type_engine,
                                                speed=speed,
                                                time=time)

        if new_commands is not None:
            print("[NEW COMMANDS] ~ ", new_commands.dict())
            mes, code = send_command(new_commands, self.IP_CONFIG)
            print(mes)

            if code == 301:
                pass
            elif code == 302:
                pass
            elif code == 404:
                pass

        else:
            print("[ERROR] SEND NEW COMMAND")
            return None

    def find_angle(self, test_vector: np.array = None):
        """ Поиск угла поворота """
        if test_vector is None:
            res_angl = search(self.my_vector, self.vector_target)
        else:
            res_angl = search(test_vector, self.vector_target)

        print("[SYSTEM LOGIC] ROBOT TURN TO ANGLE ~ ", res_angl[0])
        return res_angl

    def command_turn(self, new_angle):
        """Формирование команды поворота"""
        time_work = float(abs(new_angle)) / self.circular_speed
        new_vector = Rotation.from_rotvec(new_angle*self.my_vector, degrees=True) #поворот вектора робота
        self.my_vector = new_vector.as_rotvec()

        if new_angle > 0: # надо перепроверить
            self.send_command_robot('left', time_work)
        else:
            self.send_command_robot('right', time_work)

    def moving_forward(self, distance, my_last_cor):
        """Формирование команды движения вперёд"""
        time_work = float(distance) / self.line_speed #время для достижения к цели

        # # V-algorithm
        # ITER_FIND_TARGET = 50
        # # dt = time_work / ITER_FIND_TARGET
        # #
        # # while ITER_FIND_TARGET > 0:
        # #     self.send_command_robot('tank', dt)
        # #
        # #     self._find_my_vector() #поиск собственного вектора
        # #     angle_to_target = self.find_angle() #поиск угла от цели
        # #
        # #     if abs(angle_to_target) > self.error_angle:
        # #         self.command_turn(angle_to_target)
        # #     ITER_FIND_TARGET -= 1
        #
        #Kalman_algorithm
        ITER_FIND_TARGET = 50
        dt = time_work / ITER_FIND_TARGET

        kl_filter = KalmanFilter() #настройка фильтера калмена
        size_prediction = 10 #количество предугаданных значений
        kalman_on = 0.1 #(0 ~ 1) периодичность срабатывания фильтра относительно от всех итераций
        iter_kalman = ITER_FIND_TARGET * kalman_on #подсчёт периодичности

        angle_error_predict = 5 #ошибка предсказания, мерреется в гпадусах

        global_iter = 0 #служебная переменная для цикла
        predict = [] #служебный массив для предсказания

        while ITER_FIND_TARGET > global_iter:
            input(("\nGO TO NEXT"))
            self.send_command_robot('tank', dt)
            my_new_coordinate = self._find_my_coordinate()

            if global_iter != iter_kalman:
                predict = kl_filter.predict(my_new_coordinate[0], my_new_coordinate[1])
            else:
                iter_predict = 0
                while size_prediction > iter_predict: #начало предсказания
                    iter_predict += 1
                    predict = kl_filter.predict(predict[0], predict[1])
                    print("[SYSTEM LOGIC] ~ KALMAN PREDICT:", predict)

                predict_vector = np.array([predict[0], predict[1]]) - self.my_coordinate.get_last_coordinate()
                angle_predict = self.find_angle(test_vector=predict_vector)

                if abs(angle_predict[0]) > angle_error_predict: #опережающая переруглировка по калмену
                    print("[SYSTEM LOGIC] ~ KALMAN OVERSHOOT", abs(angle_predict[0]) - angle_error_predict, "angle")
                    real_angle = self.find_angle()
                    input(("\nGO TO NEXT"))
                    self.command_turn(real_angle[0])
                else:
                    print("[SYSTEM LOGIC] ~ KALMAN NOT OVERSHOOT", abs(angle_predict[0]) - angle_error_predict)

                angle_to_target = self.find_angle() #поиск угла от цели
                if abs(angle_to_target[0]) > self.error_angle: #провекрка переругулировки
                    input(("\nGO TO NEXT"))
                    self.command_turn(angle_to_target[0])

                kl_filter.kf.init(4, 2) #обновление калмена фильтера
                ITER_FIND_TARGET -= global_iter
                global_iter = 0

            #проверки для выхода из цикла
            self.vector_target = self.my_target_coordinate - my_new_coordinate
            if self.error_rate >= cdist(self.my_vector[None], self.vector_target[None], metric="euclidean")[0]:
                break
            elif distance <= self._path_traveled(my_new_coordinate, my_last_cor):
                break
            else:
                global_iter += 1

    def attack_target(self, distance, my_last_cor):
        """Атакует цель"""
        angle_between = self.find_angle()
        if abs(angle_between[0]) > self.error_angle:
            input(("\nGO TO NEXT"))
            self.command_turn(angle_between[0]) # первичный поворот

        self.moving_forward(distance, my_last_cor) #движение вперёд

    def preparing_for_the_start(self, coordinate_tar):
        """Настройка параметров перед атакой цели"""
        my_last_coordinate: np.array = self.my_coordinate.get_last_coordinate()
        if coordinate_tar is not None:
            self.my_target_coordinate = np.array([coordinate_tar[0], coordinate_tar[0]])
            self.vector_target = self.my_target_coordinate - my_last_coordinate
            self.modul_distance_target = cdist(self.my_vector[None], self.vector_target[None], metric="euclidean")[0]

        print("\n[SYSTEM LOGIC] ~ ROBOT GO NEW TARGET", "COORDINATE", self.my_target_coordinate)
        print("[SYSTEM LOGIC] ~ PARAMETRS GO TARGET", "VECTOR =", self.vector_target, "DISTANCE", self.modul_distance_target)
        return my_last_coordinate

    def start_new_target(self, coordinate_tar):
        """запуск алгоритма движения к цели"""
        if self.my_target_coordinate is None:
            my_last_cor = self.preparing_for_the_start(coordinate_tar)

            distance_path: float = 0
            while True:
                self.attack_target(self.modul_distance_target, my_last_cor) #логика движения
                self._find_my_coordinate()

                self.vector_target = self.my_target_coordinate - self.my_coordinate.get_last_coordinate()
                self.modul_distance_target = cdist(self.my_vector[None], self.vector_target[None], metric="euclidean")[0]

                if self.modul_distance_target < self.error_rate:
                    break
                else:
                    my_last_cor = self.preparing_for_the_start(coordinate_tar)

            self.my_target_coordinate = None
            self.vector_target = None
            self.modul_distance_target = None