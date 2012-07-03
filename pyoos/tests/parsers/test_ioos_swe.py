import unittest
from pyoos.tests.utils import resource_file
from pyoos.parsers.ioos_swe import IoosSwe
import pytz
from datetime import datetime

class SweIoosTest(unittest.TestCase):

    def test_timeseries_multiple_sensor_data_choice(self):
        swe = open(resource_file('swe_timeseries_multiple_sensor.xml'), "rU").read()
        ios = IoosSwe(swe)

        # The BBOX defined in GML
        assert list(ios.observations['TimeSeries_1'].bbox.exterior.coords)[0] == (-78.5, 32.5)

        # featureOfInterest 
        assert ios.observations['TimeSeries_1'].feature_type == 'timeSeries'
        # Location defined within featureOfInterest
        assert ios.observations['TimeSeries_1'].feature.geo.x == -78.5
        assert ios.observations['TimeSeries_1'].feature.geo.y == 32.5

        data = ios.observations['TimeSeries_1'].feature.data
        data.calculate_bounds()

        # Depth range
        assert data.depth_range[0] == -4
        assert data.depth_range[-1] == 10

        # Time range
        assert data.time_range[0] == datetime(2009,05,23, tzinfo=pytz.utc)
        assert data.time_range[-1] == datetime(2009,05,23,2, tzinfo=pytz.utc)

        # Bbox is one point for this test, since it is a single point
        assert data.bbox.x == -78.5
        assert data.bbox.y == 32.5

    def test_timeseries_single_sensor(self):
        swe = open(resource_file('swe_timeseries_single_sensor.xml'), "rU").read()
        ios = IoosSwe(swe)

        # The BBOX defined in GML
        assert list(ios.observations['TimeSeries_1'].bbox.exterior.coords)[0] == (-78.5, 32.5)

        # featureOfInterest 
        assert ios.observations['TimeSeries_1'].feature_type == 'timeSeries'
        # Location defined within featureOfInterest
        assert ios.observations['TimeSeries_1'].feature.geo.x == -78.5
        assert ios.observations['TimeSeries_1'].feature.geo.y == 32.5

        data = ios.observations['TimeSeries_1'].feature.data
        data.calculate_bounds()

        # Depth range
        assert data.depth_range[0] == 10
        assert data.depth_range[-1] == 10

        # Time range
        assert data.time_range[0] == datetime(2009,05,23, tzinfo=pytz.utc)
        assert data.time_range[-1] == datetime(2009,05,23,2, tzinfo=pytz.utc)

        # Bbox is one point for this test, since it is a single point
        assert data.bbox.x == -78.5
        assert data.bbox.y == 32.5