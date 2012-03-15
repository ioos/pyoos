from pyoos.cdm.features.feature import Feature
from pyoos.cdm.utils.structure_data import StructureData

class Point(Feature):
	"""
		A collection of observations at one time and location.
		ie. An instantaneous reading of multiple parameters from a sensor
	"""

	def __init__(self):
		self._data = StructureData()
		return None


	def get_location(self):
		return self._location
	def set_location(self, location):
		self._location = location
	location = property(get_location, set_location)

	def get_time(self):
		return self._time
	def set_time(self, time):
		self._time = time
	time = property(get_time, set_time)

	def get_data(self):
		return self._data