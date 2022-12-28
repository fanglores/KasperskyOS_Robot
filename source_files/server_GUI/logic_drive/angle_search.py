import numpy as np
from numpy.linalg import norm
import math


class Direction:
	vector: np.array
	modl: float

	def __init__(self, vector: np.array):
		self.vector = vector
		self.modl = norm(self.vector)
	
	def angle(self):
		if self.vector[0] > 0 and self.vector[1] >= 0:
			return math.atan(self.vector[1] / self.vector[0])
		elif self.vector[0] > 0 and self.vector[1] < 0:
			return (math.atan(self.vector[1] / self.vector[0]) + 2 * math.pi)
		elif self.vector[0] <0:
			return (math.atan(self.vector[1] / self.vector[0]) + math.pi)
		elif self.vector[0] == 0 and self.vector[1] > 0:
			return math.pi / 2
		elif self.vector[0] == 0 and self.vector[1] < 0:
			return (3 * math.pi / 2)
		else:
			return None


def search(vector1, vector2):
	actualVector = Direction(vector1) #вектор направления робота
	targetVector = Direction(vector2) #вектор направления к цели
	act_tan = actualVector.angle()
	tar_tan = targetVector.angle()
	if act_tan - tar_tan == 0:
		return 0
	else:
		return ((act_tan - tar_tan) * 180 / math.pi), targetVector.modl