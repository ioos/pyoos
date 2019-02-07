from __future__ import absolute_import, division, print_function

import datetime
import unittest

import pytz
from paegan.cdm.dsg.collections.station_collection import StationCollection

from pyoos.parsers.hads import HadsParser


class HadsParserTest(unittest.TestCase):
    def setUp(self):
        self.hp = HadsParser()

        # captured metadata 26 July 2013 for stations ['DD182264', '17BC752E', 'CE4D0268']
        self.metadata = u"|17BC752E|WKGR1|CHIPUXET RIVER AT WEST KINGSTON|41 28 56|-71 33 06|BOX|RI|USGS01|SI|83  |002840|60|HG|15,-9|0.01,-9|0.0|13|0.0|-0.01|VB|60,-9|0.3124,-9|0.311|28|0.0|0.0|\r\n|CE4D0268|FOXR1|FOXPOINT HURRICANE BARRIER|41 48 57|-71 24 07|BOX|RI|CENED1|SU|161 |000100|30|HM|60,-9|0.01,-9|0.0|1|0.0|0.0|PA|60,-9|0.01,-9|0.0|1|0.0|0.0|TA|60,-9|0.1,-9|0.0|1|0.0|0.0|US|60,-9|1,-9|0.0|1|0.0|0.0|UD|60,-9|1,-9|0.0|1|0.0|0.0|\r\n|DD182264|USQR1|USQUEPAUG RIVER NEAR USQUEPAUG|41 28 36|-71 36 19|BOX|RI|USGS01|SI|83  |005830|60|HG|15,-9|0.01,-9|0.0|13|0.0|0.0|VB|60,-9|0.3124,-9|0.311|58|0.0|0.0|\r\n"  # noqa

        # captured data 26 July 2013 for stations ['DD182264', '17BC752E', 'CE4D0268']
        self.raw_data = u"CE4D0268|FOXR1|HM|2013-07-26 16:30|4.94|  |\r\nCE4D0268|FOXR1|HM|2013-07-26 17:00|4.41|  |\r\nCE4D0268|FOXR1|PA|2013-07-26 16:30|29.93|  |\r\nCE4D0268|FOXR1|PA|2013-07-26 17:00|29.93|  |\r\nCE4D0268|FOXR1|TA|2013-07-26 16:30|66.20|  |\r\nCE4D0268|FOXR1|TA|2013-07-26 17:00|67.30|  |\r\nCE4D0268|FOXR1|US|2013-07-26 16:30|5.00|  |\r\nCE4D0268|FOXR1|US|2013-07-26 17:00|8.00|  |\r\nCE4D0268|FOXR1|UD|2013-07-26 16:30|358.00|  |\r\nCE4D0268|FOXR1|UD|2013-07-26 17:00|353.00|  |\r\nDD182264|USQR1|HG|2013-07-26 16:30|3.07|  |\r\nDD182264|USQR1|HG|2013-07-26 16:45|3.07|  |\r\n"  # noqa

    def test_parse(self):
        station_collection = self.hp.parse(
            self.metadata, self.raw_data, None, (None, None)
        )
        assert isinstance(station_collection, StationCollection)

        station_collection.calculate_bounds()
        assert station_collection.size == 3

    def test__parse_metadata(self):
        res = {
            u"17BC752E": {
                "channel": u"83  ",
                "hsa": u"BOX",
                "init_transmit": u"002840",
                "latitude": 41.48222222222222,
                "location_text": u"CHIPUXET RIVER AT WEST KINGSTON",
                "longitude": -70.44833333333334,
                "manufacturer": u"SI",
                "nesdis_id": u"17BC752E",
                "nwsli": u"WKGR1",
                "owner": u"USGS01",
                "state": u"RI",
                "variables": {
                    u"HG": {
                        "base_elevation": 0.0,
                        "coefficient": u"0.01,-9",
                        "constant": u"0.0",
                        "data_interval": u"15,-9",
                        "gauge_correction": -0.01,
                        "time_offset": u"13",
                    },
                    u"VB": {
                        "base_elevation": 0.0,
                        "coefficient": u"0.3124,-9",
                        "constant": u"0.311",
                        "data_interval": u"60,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"28",
                    },
                },
            },
            u"CE4D0268": {
                "channel": u"161 ",
                "hsa": u"BOX",
                "init_transmit": u"000100",
                "latitude": 41.81583333333333,
                "location_text": u"FOXPOINT HURRICANE BARRIER",
                "longitude": -70.59805555555556,
                "manufacturer": u"SU",
                "nesdis_id": u"CE4D0268",
                "nwsli": u"FOXR1",
                "owner": u"CENED1",
                "state": u"RI",
                "variables": {
                    u"HM": {
                        "base_elevation": 0.0,
                        "coefficient": u"0.01,-9",
                        "constant": u"0.0",
                        "data_interval": u"60,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"1",
                    },
                    u"PA": {
                        "base_elevation": 0.0,
                        "coefficient": u"0.01,-9",
                        "constant": u"0.0",
                        "data_interval": u"60,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"1",
                    },
                    u"TA": {
                        "base_elevation": 0.0,
                        "coefficient": u"0.1,-9",
                        "constant": u"0.0",
                        "data_interval": u"60,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"1",
                    },
                    u"UD": {
                        "base_elevation": 0.0,
                        "coefficient": u"1,-9",
                        "constant": u"0.0",
                        "data_interval": u"60,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"1",
                    },
                    u"US": {
                        "base_elevation": 0.0,
                        "coefficient": u"1,-9",
                        "constant": u"0.0",
                        "data_interval": u"60,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"1",
                    },
                },
            },
            u"DD182264": {
                "channel": u"83  ",
                "hsa": u"BOX",
                "init_transmit": u"005830",
                "latitude": 41.47666666666667,
                "location_text": u"USQUEPAUG RIVER NEAR USQUEPAUG",
                "longitude": -70.39472222222223,
                "manufacturer": u"SI",
                "nesdis_id": u"DD182264",
                "nwsli": u"USQR1",
                "owner": u"USGS01",
                "state": u"RI",
                "variables": {
                    u"HG": {
                        "base_elevation": 0.0,
                        "coefficient": u"0.01,-9",
                        "constant": u"0.0",
                        "data_interval": u"15,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"13",
                    },
                    u"VB": {
                        "base_elevation": 0.0,
                        "coefficient": u"0.3124,-9",
                        "constant": u"0.311",
                        "data_interval": u"60,-9",
                        "gauge_correction": 0.0,
                        "time_offset": u"58",
                    },
                },
            },
        }

        parsed = self.hp._parse_metadata(self.metadata)
        assert parsed == res

    def test__parse_data(self):
        res = {
            u"CE4D0268": [
                (
                    u"HM",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    4.94,
                ),
                (
                    u"HM",
                    datetime.datetime(2013, 7, 26, 17, 0).replace(
                        tzinfo=pytz.utc
                    ),
                    4.41,
                ),
                (
                    u"PA",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    29.93,
                ),
                (
                    u"PA",
                    datetime.datetime(2013, 7, 26, 17, 0).replace(
                        tzinfo=pytz.utc
                    ),
                    29.93,
                ),
                (
                    u"TA",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    66.20,
                ),
                (
                    u"TA",
                    datetime.datetime(2013, 7, 26, 17, 0).replace(
                        tzinfo=pytz.utc
                    ),
                    67.30,
                ),
                (
                    u"US",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    5.00,
                ),
                (
                    u"US",
                    datetime.datetime(2013, 7, 26, 17, 0).replace(
                        tzinfo=pytz.utc
                    ),
                    8.00,
                ),
                (
                    u"UD",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    358.00,
                ),
                (
                    u"UD",
                    datetime.datetime(2013, 7, 26, 17, 0).replace(
                        tzinfo=pytz.utc
                    ),
                    353.00,
                ),
            ],
            u"DD182264": [
                (
                    u"HG",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    3.07,
                ),
                (
                    u"HG",
                    datetime.datetime(2013, 7, 26, 16, 45).replace(
                        tzinfo=pytz.utc
                    ),
                    3.07,
                ),
            ],
        }

        parsed = self.hp._parse_data(self.raw_data, None, (None, None))
        assert parsed == res

    def test__parse_data_with_var_filter(self):
        res = {
            u"CE4D0268": [
                (
                    u"HM",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    4.94,
                ),
                (
                    u"HM",
                    datetime.datetime(2013, 7, 26, 17, 0).replace(
                        tzinfo=pytz.utc
                    ),
                    4.41,
                ),
                (
                    u"UD",
                    datetime.datetime(2013, 7, 26, 16, 30).replace(
                        tzinfo=pytz.utc
                    ),
                    358.00,
                ),
                (
                    u"UD",
                    datetime.datetime(2013, 7, 26, 17, 0).replace(
                        tzinfo=pytz.utc
                    ),
                    353.00,
                ),
            ]
        }

        parsed = self.hp._parse_data(
            self.raw_data, [u"HM", u"UD"], (None, None)
        )
        assert parsed == res
