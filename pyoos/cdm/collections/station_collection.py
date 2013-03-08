from pyoos.cdm.collections.nested_point_collection import NestedPointCollection
from pyoos.cdm.features.station import Station

class StationCollection(NestedPointCollection):
	""" Collection of Station features """
	def __init__(self, **kwargs):
		super(StationCollection,self).__init__(**kwargs)
