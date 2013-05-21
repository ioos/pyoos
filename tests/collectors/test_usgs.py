import unittest
from pyoos.collectors.usgs.usgs import USGSCollector
from datetime import datetime, timedelta

class USGSTest(unittest.TestCase):

	def setUp(self):
		self._usgs = USGSCollector()

	def test_by_bbox(self):
		"""
			test station cdm returned from usgs
		"""

		collection = self._usgs.get_stations_by_bbox(48,46,-85,-87)

		assert collection is not None

		collection.calculate_bounds()

		assert collection.size == len(collection.time_range) == collection.point_size == 4

		# test period_hours
		collection = self._usgs.get_stations_by_bbox(48,46,-85,-87,period_hours=6)

		assert collection is not None

		collection.calculate_bounds()

		assert collection.size == 4
		assert len(collection.time_range) == collection.point_size

	def test_by_state(self):
		"""
			test station cdm returned from usgs
		"""

		collection = self._usgs.get_stations_by_state('co',period_days=1)

		assert collection is not None

		collection.calculate_bounds()

		#assert collection.size == 387
		assert len(collection.time_range) == collection.point_size

	def test_by_site_code(self):
		"""
			test station cdm returned using site code
		"""

		station = self._usgs.get_station('04001000')

		assert station is not None

		station.calculate_bounds()

		assert station.uid == '04001000'
		assert station.name == 'WASHINGTON CREEK AT WINDIGO, MI'
		assert str(station.location) == 'POINT (-89.1459196999999932 47.9212792000000007)'

		start_dt = datetime.today() - timedelta(days=1)
		station2 = self._usgs.get_station('04001000', startDT=start_dt)

		assert station2 is not None

		station2.calculate_bounds()

		assert station2.uid == '04001000'
		assert station2.name == 'WASHINGTON CREEK AT WINDIGO, MI'
		assert str(station2.location) == 'POINT (-89.1459196999999932 47.9212792000000007)'
		assert station.size < station2.size

		start_dt = datetime.today() - timedelta(days=3)
		end_dt = datetime.today() - timedelta(days=2)

		station3 = self._usgs.get_station('04001000', startDT=start_dt, endDT=end_dt)

		assert station3 is not None

		station3.calculate_bounds()

		assert station3.uid == '04001000'
		assert station3.name == 'WASHINGTON CREEK AT WINDIGO, MI'
		assert str(station3.location) == 'POINT (-89.1459196999999932 47.9212792000000007)'
		assert station.size < station3.size



