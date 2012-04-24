class FeatureCollection(object):
	"""
		A collection of Features
		All Features in a FeatureCollection must be of the same type
	"""

	def __init__(self):
		pass

	def get_type(self):
		return self._type
