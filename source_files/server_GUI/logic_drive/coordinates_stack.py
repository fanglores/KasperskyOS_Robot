import numpy as np


class CoordinatesStack:
	new_coordinate: np.array
	old_coordinate: np.array

	def __init__(self, all_coordinate=None):
		self.new_coordinate = np.array([])
		self.new_coordinate = np.vander(self.new_coordinate, 2)

		if all_coordinate is not None: #переделать
			self.new_coordinate = all_coordinate

		# if all_coordinate is not None:
		# 	for one_coordinate in all_coordinate:
		# 		self.new_coordinate = np.append(self.new_coordinate, one_coordinate, axis=0)

	def add_new_coordinates(self, coordinates):
		self.new_coordinate = np.append(self.new_coordinate, [[coordinates[0], coordinates[1]]], axis=0)

	def clear_all_command(self):
		self.new_coordinate = np.array([])

	def get_last_coordinate(self):
		return self.new_coordinate[-1]

	def delete_new_coordinate(self, index_coordinate):
		try:
			self.old_coordinate = np.append(self.old_coordinate, self.new_coordinate[index_coordinate])
			self.new_coordinate = np.delete(self.new_coordinate, index_coordinate)
			print("[SYSTEM] ~ OK DELETE COORDINATE")
		except:
			print("[SYSTEM] ~ BAD DELETE COORDINATE")

