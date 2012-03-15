class FeatureCollection:
	"""
		A collection of Features
		All Features in a FeatureCollection must be of the same type
	"""

	def __init__(self, elements):
		self._type = elements[0].type

	def get_type(self):
		return self._type
