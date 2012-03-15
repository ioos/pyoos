from pyoos.cdm.collections.feature_collection import FeatureCollection

class PointCollection(FeatureCollection):
	"""
		A collection of Points
	"""

	def __init__(self):
		self.data = StructureData()
		return None
