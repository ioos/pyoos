import unittest
from pyoos.collectors.usgs import USGSCollector

class USGSTest(unittest.TestCase):

	def setUp(self):
		self._usgs = USGSCollector()

	def test_by_bbox(self):
		"""
			test station cdm returned from usgs
		"""

		collection = self._usgs.get_stations_by_bbox(50,48,-80,-82)

		assert collection is not None

		collection.calculate_bounds()

		print collection.size
		print collection.bbox.bounds
		print collection.bbox.area
		print collection.bbox.length
		print collection.depth_range
		print len(collection.time_range)
		print collection.point_size
		