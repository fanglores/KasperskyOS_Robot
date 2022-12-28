# Система управления робот на основе KasperskyOS c помощью веб камеры

## Описание проекта

В рамках летнего хакатона от Kasperky был создан протатип решения удалённого управления IoT устройства на KasperskyOS через TCP соединение

## Программный стек

- OpenCV 4.6
- Tensorflow-CPU 2.9.1
- Socket
- Numpy
- Sympy
- Pydantic
- Flask 2.0

## Разработано:
1. [Алгоритм движения робота](/logic_drive), который включает в себя метод Калмена для стабилизации движения 
2. [Программа поиска целей робота](/camera_robot_tracing), целями робота выступают разноцветные стикеры, также задавать цели можно кликая на картинку выдоваемой камерой
3. [Нейронная сеть](/camera_robot_tracing/mlModel.py), которая находит робота на изображении by AnimeBit
4. [TCP соединение](/connect_robot), отправляет команды роботу
5. [Веб приложение](server_robot.py), веб интерфейс с выводом камеры (не протестировано)
6. [Код Робота](https://github.com/fanglores/Kaspersky-Lab-Practics)

© eliss-good, Moscow Aviation Institute feat. Kaspersky Lab 
Moscow, 2022
