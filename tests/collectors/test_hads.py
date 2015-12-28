from __future__ import (absolute_import, division, print_function)

import unittest
from pyoos.collectors.hads.hads import Hads


class HadsTest(unittest.TestCase):

    def setUp(self):
        self.c = Hads()

        # this is a unit test.  don't hit any urls
        def list_vars(station_codes):
            return set([u'VB', u'DJ', u'DH', u'TW', u'HP', u'UP', u'US', u'PC', u'PA', u'HT', u'UD', u'TA'])
        self.c._list_variables = list_vars

        def state_urls():
            return ["http://amazon.nws.noaa.gov/hads/charts/RI.html"]
        self.c._get_state_urls = state_urls

        def get_stations_for_state(url):
            # all RI stations
            return ['17E3D706', '16C9437A', '1732F0EA', '16C95EDE', '17BC53C2', '17B56004', 'CE4D0268', '1732E39C', '3B0335EE', '3B0211F8', '83779774', 'CD0362DC', 'CD035746', 'DD182264', '16C91306', 'CE2F83BA', '17BC752E', 'CE467750', '1789841A']
        self.c._get_stations_for_state = get_stations_for_state

    def test_set_bbox_property_clears_cached_station_codes(self):
        self.c.station_codes = [1, 2]
        self.c.bbox = (1, 2, 3, 4)

        assert self.c.station_codes is None

    def test_set_features_property_clears_cached_station_codes(self):
        self.c.station_codes = [1, 2]
        self.c.features = ["one", "two"]

        assert self.c.station_codes is None

    def test_list_features(self):
        codes = self.c.list_features()
        assert 'DD182264' in codes

    def test_feature_filter(self):
        features = ['DD182264', '17BC752E', 'CE4D0268']
        self.c.filter(features=features)

        codes = self.c.list_features()

        assert set(codes) == set(features)
