from __future__ import (absolute_import, division, print_function)

import unittest
import pytest

from pyoos.collectors.awc.awc_rest import AwcRest
from paegan.cdm.dsg.collections.station_collection import StationCollection


class AwcRestTest(unittest.TestCase):

    def setUp(self):
        self.c = AwcRest()

    def test_nwc_stations(self):
        stations = self.c.stations
        assert stations[0] == 'AAAD'
        assert stations[-1] == 'ZYYY'

    def test_bbox_filter_raw(self):
        self.c.filter(bbox=(-80, 30, -60, 50))
        response = self.c.raw()
        assert '<response xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XML-Schema-instance" version="1.2" xsi:noNamespaceSchemaLocation="http://aviationweather.gov/adds/schema/metar1_2.xsd">' in response[0]

    def test_bigbbox_filter_paegan(self):
        self.c.filter(bbox=(-80, 30, -60, 50))
        response = self.c.collect()
        assert type(response) == StationCollection

    def test_smallbbox_filter_paegan(self):
        self.c.filter(bbox=(-74, 41, -73, 43))
        response = self.c.collect()
        assert type(response) == StationCollection
