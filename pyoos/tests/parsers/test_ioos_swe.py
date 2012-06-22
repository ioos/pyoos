import unittest
from pyoos.tests.utils import resource_file
from pyoos.parsers.ioos_swe import IoosSwe

class SweIoosTest(unittest.TestCase):

    def test_timeseries_multiple_sensor(self):
        swe = open(resource_file('swe_timeseries_multiple_sensor.xml'), "rU").read()
        ios = IoosSwe(swe)

        assert ios.observations['TimeSeries_1'].feature.geo.x == -78.5
        assert ios.observations['TimeSeries_1'].feature.geo.y == 32.5