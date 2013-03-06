
import unittest
from datetime import date, datetime
from pytest import raises
from pyoos.collectors.nerrs.nerrs import NerrsWSDL
from shapely.geometry import Point

class NerrTest(unittest.TestCase):

	def setUp(self):
		self.nerrs = NerrsWSDL()

	def test_get_station_cdm(self):
		"""
			test the station cdm returned from nerrs
		"""

		station = self.nerrs.get_station('acebbwq', site_id='ace', min_date='02/06/2013', max_date='02/10/2013')

		assert station is not None

		station.calculate_bounds()

		assert station.description == 'ace-acebbwq'
		assert station.name == 'Big Bay'
		assert station.uid == 'acebbwq'
		assert station.type == 'timeSeries'
		assert str(station.bbox) == 'POINT (80.3241000000000014 32.4941000000000031)'

		assert station.size == 39

		# print dir(station.get_time_range())
		# print station.get_time_range()
		# print station.elements

		alist = list()
		for m in station.get_unique_members():
			alist.append(m['name'])
		assert alist.index('Temp') >= 0
		assert alist.index('Sal') >= 0
		assert alist.index('DO_pct') >= 0
		assert alist.index('SpCond') >= 0
		assert alist.index('DO_mgl') >= 0
		assert alist.index('pH') >= 0
		assert alist.index('Turb') >= 0

		# depth bounds
		assert station.depth_range[0] == 1.67
		assert station.depth_range[station.size-1] == 3.53

		# time bounds
		assert station.time_range[0].strftime('%m/%d/%Y %H:%M') == '02/06/2013 05:00'
		assert station.time_range[station.size-1].strftime('%m/%d/%Y %H:%M') == '02/06/2013 14:30'

	def test_get_stations_bbox(self):
		"""
			test getting stations by passing in a bbox
			south=29, west=85, north=30, east=86
		"""

		collection = self.nerrs.get_stations_by_bbox(29.0,86.0,30.0,85.0)

		assert collection is not None

		collection.calculate_bounds()

		assert collection.size == 5

		assert collection.bbox.bounds == (85.0196, 29.6079, 85.089, 29.7791)
		assert collection.bbox.area == 0.011881280000000213
		assert collection.bbox.length == 0.4812000000000012
		assert collection.depth_range is not None
		assert len(collection.time_range) > 0
		assert datetime(2013,2,6,3,0) in collection.time_range
		assert collection.point_size == 1668

	def test_get_stations_latlon(self):
		"""
			test getting stations by passing in a single lat-lon pair
			test getting stations by passing in several lat-lon pairs
			lat=32.5485,32.5233,29.7021,29.7021
			lon=80.5036,80.3568,80.3568,84.8802
		"""

		collection = self.nerrs.get_stations_by_latlon(32.5485,80.5036)

		assert collection is not None

		collection.calculate_bounds()

		assert collection.size == 1

		assert collection.bbox.bounds == (80.5036, 32.5485, 80.5036, 32.5485)
		assert collection.bbox.area == 0.0
		assert collection.bbox.length == 0.0
		assert len(collection.depth_range) == 932
		assert len(collection.time_range) == 932
		assert collection.point_size == 932

		collection = self.nerrs.get_stations_by_latlon('32.5485,32.5233,29.7021,29.7021','80.5036,80.3568,80.3568,84.8802')

		assert collection is not None

		collection.calculate_bounds()

		assert collection.size == 5

		assert collection.bbox.bounds == (80.3568, 29.7021, 84.8802, 32.5485)
		assert collection.bbox.area == 12.875405759999966
		assert collection.bbox.length == 14.739599999999982
		assert collection.depth_range is not None
		assert len(collection.depth_range) == 2928
		assert len(collection.time_range) == 4079
		assert collection.point_size == 4079
