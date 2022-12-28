import numpy as np

from cofig_server import flask_app, cross_origin
from flask import jsonify, request

from pydantic import BaseModel, constr
from typing import Optional

from main import WorkedSystem

""" JSON MODEL POST REQUEST """

class RobotCommandSchema(BaseModel):
    command_robot: constr(min_length=2)


class RobotCoordinateSchema(BaseModel):
    x_cr: Optional[int]
    y_cr: Optional[int]
    size_image: list


"""  API CONFIG  """


@flask_app.route('/api/robot', methods=['POST'])
def robot_web():
    if request.method == 'POST':
        try:
            new_command = RobotCommandSchema(**request.get_json())

            if new_command.command_robot == 'color':
                wrk_system.type_drive = 'color'

            elif new_command.command_robot == 'dot':
                wrk_system.type_drive = 'dot'
                wrk_system.start_touch_target()

            """отправка комманд на исполение"""
            return jsonify("GOOD"), 200
        except:
            return jsonify({"ERROR": "COMMAND ERROR"}), 401


@flask_app.route('/api/coordinate_robot', methods=['POST'])
def robot_coordinate():
    if request.method == 'POST':
        try:
            new_command = RobotCoordinateSchema(**request.get_json())
            correct_k_x = new_command.size_image[0] / 640
            correct_k_y = new_command.size_image[1] / 480

            new_x = int(new_command.x_cr / correct_k_x)
            new_y = int(new_command.y_cr / correct_k_y)

            array_dot = np.array([new_x, new_y])

            print(new_x, new_y)
            # wrk_system.add_new_touch(array_dot)
            """отправка комманд на исполение"""
            return jsonify("GOOD"), 200
        except:
            return jsonify({"ERROR": "COMMAND ERROR"}), 401

if __name__ == '__main__':
    wrk_system = WorkedSystem()
    flask_app.run(host='0.0.0.0', debug=False)







