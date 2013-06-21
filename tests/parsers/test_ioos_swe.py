import unittest
from tests.utils import resource_file
from pyoos.parsers.ioos_swe import IoosSwe
import pytz
from datetime import datetime
from shapely.geometry import Point

from pyoos.parsers.ioos.get_observation import IoosGetObservation

class SweIoosTest(unittest.TestCase):

    def test_o_and_m_get_observation(self):
        data = open(resource_file(os.path.join('ioos_swe','OM-GetObservation.xml')), "rU").read()
        
        d = IoosGetObservation(data)
        assert d.ioos_version == "1.0"
        assert len(d.observations) == 1

        ts = d.observations[0]
        assert ts.description == "Observations at point station urn:ioos:station:wmo:41001, 150 NM East of Cape \
        HATTERAS. Observations at point station urn:ioos:station:wmo:41002, S HATTERAS \
        - 250 NM East of Charleston, SC"
        assert ts.begin_position == datetime(2009, 5, 23, 0, tzinfo=pytz.utc)
        assert ts.end_position == datetime(2009, 5, 23, 2, tzinfo=pytz.utc)
        assert sorted(ts.procedures) == sorted(["urn:ioos:station:wmo:41001","urn:ioos:station:wmo:41002"])
        assert sorted(ts.observedProperties) == sorted(["http://mmisw.org/ont/cf/parameter/air_temperature",
                                                       "http://mmisw.org/ont/cf/parameter/wind_speed",
                                                       "http://mmisw.org/ont/cf/parameter/wind_direction",
                                                       "http://mmisw.org/ont/cf/parameter/sea_water_temperature",
                                                       "http://mmisw.org/ont/cf/parameter/dissolved_oxygen"])
        assert ts.feature_type == "timeSeries"
       
        assert ts.bbox_srs == "EPSG:4326"
        assert ts.bbox = (-75.42, 32.38, -72.73, 34.7)

        assert ts.location = {  "urn:ioos:station:wmo:41001" : Point(-72.73, 34.7),
                                "urn:ioos:station:wmo:41002" : Point(-75.415, 32.382) }


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