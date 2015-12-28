from __future__ import (absolute_import, division, print_function)

import os
import unittest
from datetime import datetime

import pytz

from tests.utils import resource_file

from pyoos.parsers.ioos.describe_sensor import IoosDescribeSensor


class IoosDescribeSensorTest(unittest.TestCase):

    def test_network(self):
        data = open(resource_file(os.path.join('ioos_swe', 'SML-DescribeSensor-Network.xml')), "rb").read()
        d    = IoosDescribeSensor(data)

        assert d.ioos_version == "1.0"
        assert d.system.name  == "urn:ioos:network:nanoos:all"
        assert d.procedures   == sorted([u'urn:ioos:station:wmo:41001', u'urn:ioos:station:wmo:41002'])
        assert d.starting     == datetime(2008, 4, 28, 8, tzinfo=pytz.utc)
        assert d.ending       == datetime(2012, 12, 27, 19, tzinfo=pytz.utc)

    def test_station(self):
        data = open(resource_file(os.path.join('ioos_swe', 'SML-DescribeSensor-Station.xml')), "rb").read()
        d = IoosDescribeSensor(data)

        assert d.ioos_version == "1.0"
        assert d.system.name == "urn:ioos:station:wmo:41001"
        assert d.variables   == sorted([u'http://mmisw.org/ont/cf/parameter/sea_water_temperature',
                                        u'http://mmisw.org/ont/cf/parameter/sea_water_salinity',
                                        u'http://mmisw.org/ont/cf/parameter/air_pressure',
                                        u'http://mmisw.org/ont/cf/parameter/air_temperature'])
        assert d.starting     == datetime(2008, 4, 28, 8, tzinfo=pytz.utc)
        assert d.ending       == datetime(2012, 12, 27, 19, tzinfo=pytz.utc)

    def test_sensor(self):
        data = open(resource_file(os.path.join('ioos_swe', 'SML-DescribeSensor-Sensor.xml')), "rb").read()
        d = IoosDescribeSensor(data)

        assert d.ioos_version == "1.0"
        assert d.system.name == "urn:ioos:sensor:us.glos:45023:sea_water_temperature"
        assert d.starting     == datetime(2013, 8, 26, 18, 10, tzinfo=pytz.utc)
        assert d.ending       == datetime(2013, 8, 26, 18, 10, tzinfo=pytz.utc)
