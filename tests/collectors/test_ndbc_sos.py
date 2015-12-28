from __future__ import (absolute_import, division, print_function)
from six import string_types

import unittest
import csv
import io
from datetime import datetime

from owslib.swe.sensor.sml import SensorML

from pyoos.collectors.ndbc.ndbc_sos import NdbcSos


class NdbcSosTest(unittest.TestCase):

    def setUp(self):
        self.c = NdbcSos()

    def test_ndbc_server_id(self):
        assert self.c.server.identification.title == "National Data Buoy Center SOS"
        assert self.c.server.identification.service == 'OGC:SOS'
        assert self.c.server.identification.version == '1.0.0'
        assert self.c.server.identification.abstract == 'National Data Buoy Center SOS'
        # assert self.c.server.identification.keywords == ['Weather', 'Ocean Currents', 'Air Temperature', 'Water Temperature', 'Conductivity', 'Salinity', 'Barometric Pressure', 'Water Level', 'Waves', 'Winds', 'NDBC']
        assert self.c.server.identification.fees == 'NONE'
        assert self.c.server.identification.accessconstraints == 'NONE'

    def test_ndbc_describe_sensor(self):
        self.c.features = ['41012']
        response = self.c.metadata(output_format='text/xml;subtype="sensorML/1.0.1"')
        assert isinstance(response, list)
        assert isinstance(response[0], SensorML)

    def test_raw_ndbc_get_observation(self):
        self.c.start_time   = datetime.strptime("2012-10-01", "%Y-%m-%d")
        self.c.end_time     = datetime.strptime("2012-10-02", "%Y-%m-%d")
        self.c.features     = ['41012']
        self.c.variables    = ['air_pressure_at_sea_level']

        response = self.c.raw(responseFormat="text/csv").decode()
        assert isinstance(response, string_types)
        """
        station_id,sensor_id,"latitude (degree)","longitude (degree)",date_time,"depth (m)","air_pressure_at_sea_level (hPa)"
        urn:ioos:station:wmo:41012,urn:ioos:sensor:wmo:41012::baro1,30.04,-80.55,2012-10-01T00:50:00Z,0.00,1009.8
        """
        data = list(csv.DictReader(io.StringIO(response)))
        assert data[0]['station_id'] == 'urn:ioos:station:wmo:41012'
        assert data[0]['sensor_id'] == 'urn:ioos:sensor:wmo:41012::baro1'
        assert data[0]['date_time'] == "2012-10-01T00:50:00Z"
        assert data[0]['depth (m)'] == "0.00"
        assert data[0]['air_pressure_at_sea_level (hPa)'] == "1009.8"

    def test_raw_ndbc_get_observation_all_stations(self):
        self.c.start_time   = datetime.strptime("2012-10-01", "%Y-%m-%d")
        self.c.end_time     = datetime.strptime("2012-10-02", "%Y-%m-%d")
        # TODO: This should not return all stations in the future.  We should make multiple requests.
        self.c.features     = ['32st0', '41012']  # Triggers network-all
        self.c.variables    = ['air_pressure_at_sea_level']

        response = self.c.raw(responseFormat="text/csv").decode()
        assert isinstance(response, string_types)

        data = list(csv.DictReader(io.StringIO(response)))
        stations = list(set([x['station_id'] for x in data]))
        # 265 stations measured air_pressure that day
        assert len(stations) == 265

        """
        station_id,sensor_id,"latitude (degree)","longitude (degree)",date_time,"depth (m)","air_pressure_at_sea_level (hPa)"
        urn:ioos:station:wmo:32st0,urn:ioos:sensor:wmo:32st0::baro1,-19.713,-85.585,2012-10-01T00:00:00Z,,1019.0
        """
        assert data[0]['station_id'] == 'urn:ioos:station:wmo:32st0'
        assert data[0]['sensor_id'] == 'urn:ioos:sensor:wmo:32st0::baro1'
        assert data[0]['date_time'] == "2012-10-01T00:00:00Z"
        assert data[0]['depth (m)'] == ""
        assert data[0]['air_pressure_at_sea_level (hPa)'] == "1019.0"

    def test_raw_ndbc_get_observation_no_stations(self):
        self.c.start_time   = datetime.strptime("2012-10-01", "%Y-%m-%d")
        self.c.end_time     = datetime.strptime("2012-10-02", "%Y-%m-%d")
        self.c.features     = []  # Triggers network-all
        self.c.variables    = ['air_pressure_at_sea_level']

        response = self.c.raw(responseFormat="text/csv").decode()
        assert isinstance(response, string_types)

        data = list(csv.DictReader(io.StringIO(response)))
        stations = list(set([x['station_id'] for x in data]))
        # 265 stations measured air_pressure that day
        assert len(stations) == 265

        """
        station_id,sensor_id,"latitude (degree)","longitude (degree)",date_time,"depth (m)","air_pressure_at_sea_level (hPa)"
        urn:ioos:station:wmo:32st0,urn:ioos:sensor:wmo:32st0::baro1,-19.713,-85.585,2012-10-01T00:00:00Z,,1019.0
        """
        assert data[0]['station_id'] == 'urn:ioos:station:wmo:32st0'
        assert data[0]['sensor_id'] == 'urn:ioos:sensor:wmo:32st0::baro1'
        assert data[0]['date_time'] == "2012-10-01T00:00:00Z"
        assert data[0]['depth (m)'] == ""
        assert data[0]['air_pressure_at_sea_level (hPa)'] == "1019.0"
