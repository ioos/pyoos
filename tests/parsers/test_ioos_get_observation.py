import os
import unittest
from datetime import datetime
from tests.utils import resource_file

import pytz
from shapely.geometry import Point, box

from paegan.cdm.dsg.features.station import Station
from paegan.cdm.dsg.features.station_profile import StationProfile
from paegan.cdm.dsg.collections.station_collection import StationCollection

from pyoos.utils.etree import etree
from pyoos.parsers.ioos.one.timeseries import TimeSeries
from pyoos.parsers.ioos.one.timeseries_profile import TimeSeriesProfile
from pyoos.parsers.ioos.get_observation import IoosGetObservation


class SweIoosTest(unittest.TestCase):

    def test_o_and_m_get_observation(self):
        data = open(resource_file(os.path.join('ioos_swe', 'OM-GetObservation.xml')), "rU").read()

        d = IoosGetObservation(data)
        assert d.ioos_version       == "1.0"
        assert len(d.observations)  == 1

        ts = d.observations[0]
        assert ts.description.replace("\n", "").replace("       ", "").replace("  -", " -") == "Observations at point station urn:ioos:station:wmo:41001, 150 NM East of Cape HATTERAS. Observations at point station urn:ioos:station:wmo:41002, S HATTERAS - 250 NM East of Charleston, SC"
        assert ts.begin_position                == datetime(2009, 5, 23, 0, tzinfo=pytz.utc)
        assert ts.end_position                  == datetime(2009, 5, 23, 2, tzinfo=pytz.utc)
        assert sorted(ts.procedures)            == sorted(["urn:ioos:station:wmo:41001", "urn:ioos:station:wmo:41002"])
        assert sorted(ts.observedProperties)    == sorted([ "http://mmisw.org/ont/cf/parameter/air_temperature",
                                                            "http://mmisw.org/ont/cf/parameter/sea_water_temperature",
                                                            "http://mmisw.org/ont/cf/parameter/wind_direction",
                                                            "http://mmisw.org/ont/cf/parameter/wind_speed",
                                                            "http://mmisw.org/ont/ioos/parameter/dissolved_oxygen"
                                                            ])
        assert ts.feature_type          == "timeSeries"

        assert ts.bbox_srs.getcode()    == "EPSG:4326"
        assert ts.bbox.equals(box(-75.42, 32.38, -72.73, 34.7))

        assert ts.location["urn:ioos:station:wmo:41001"].equals(Point(-72.73, 34.7))
        assert ts.location["urn:ioos:station:wmo:41002"].equals(Point(-75.415, 32.382))

    def test_timeseries_multi_station_multi_sensor(self):
        swe = open(resource_file('ioos_swe/SWE-MultiStation-TimeSeries.xml')).read()
        data_record = etree.fromstring(swe)
        collection = TimeSeries(data_record).feature

        assert isinstance(collection, StationCollection)
        assert len(collection.elements) == 3

    def test_timeseries_single_station_single_sensor(self):
        swe = open(resource_file('ioos_swe/SWE-SingleStation-SingleProperty-TimeSeries.xml')).read()
        data_record = etree.fromstring(swe)
        station = TimeSeries(data_record).feature

        assert isinstance(station, Station)

        assert station.uid          == "urn:ioos:station:wmo:41001"
        assert station.name         == "wmo_41001"
        assert station.location.x   == -75.415
        assert station.location.y   == 32.382
        assert station.location.z   == 0.5

        assert sorted(map(lambda x: x.time.strftime("%Y-%m-%dT%H:%M:%SZ"), station.elements)) == sorted(["2009-05-23T00:00:00Z", "2009-05-23T01:00:00Z", "2009-05-23T02:00:00Z"])

        first_members = station.elements[0].members
        assert sorted(map(lambda x: x['value'],    first_members)) == sorted([2.0, 15.4, 280])
        assert sorted(map(lambda x: x['standard'], first_members)) == sorted([  "http://mmisw.org/ont/cf/parameter/air_temperature",
                                                                                "http://mmisw.org/ont/cf/parameter/wind_to_direction",
                                                                                "http://mmisw.org/ont/cf/parameter/wind_speed"])

    def test_timeseries_profile_single_station(self):
        swe = open(resource_file('ioos_swe/SWE-SingleStation-TimeSeriesProfile_QC.xml')).read()
        data_record = etree.fromstring(swe)
        station = TimeSeriesProfile(data_record).feature

        assert isinstance(station, StationProfile)

        assert station.uid        == "urn:ioos:station:wmo:41001"
        assert station.name       == "wmo_41001"
        assert station.location.x == -75.415
        assert station.location.y == 32.382
        assert station.location.z == 0.5

        # should have three profiles
        assert len(station.elements) == 3
        station.calculate_bounds()

        # should all be at the same point
        bounds = station.get_bbox()
        assert isinstance(bounds, Point)
        assert bounds.x == -75.415
        assert bounds.y == 32.382

        # time
        time_range = station.get_time_range()
        assert time_range[0].strftime("%Y-%m-%dT%H:%M:%SZ") == "2009-05-23T00:00:00Z"
        assert time_range[-1].strftime("%Y-%m-%dT%H:%M:%SZ") == "2009-05-23T02:00:00Z"

        # depth bounds
        depth_range = station.get_depth_range()
        assert depth_range[0] == -39.5
        assert depth_range[-1] == -4.5

        # spot check values
        profile = station.elements[0]

        assert profile.time.strftime("%Y-%m-%dT%H:%M:%SZ") == "2009-05-23T00:00:00Z"
        assert len(profile.elements) == 4
        assert [e.location.z for e in profile.elements] == [-39.5, -19.5, -9.5, -4.5]

        assert len(profile.elements[0].members) == 2
        assert [m['name'] for m in profile.elements[0].members] == ['direction_of_sea_water_velocity', 'sea_water_speed']
        assert [m['value'] for m in profile.elements[0].members] == [352.0, 9.6]

        sensor = station.sensors['wmo_41001_sensor1']
        assert 'sensor_orientation' in sensor
        assert sensor['sensor_orientation']['X']['name'] == 'platform_pitch_angle'
        assert sensor['sensor_orientation']['Y']['name'] == 'platform_roll_angle'
        assert sensor['sensor_orientation']['Z']['name'] == 'platform_orientation'
