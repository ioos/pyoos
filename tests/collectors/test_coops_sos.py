import unittest
import csv
import StringIO
from datetime import datetime

from owslib.swe.sensor.sml import SensorML

from pyoos.collectors.coops.coops_sos import CoopsSos


class CoopsSosTest(unittest.TestCase):

    def setUp(self):
        self.c = CoopsSos()

    def test_coops_server_id(self):
        assert self.c.server.identification.title == "NOAA.NOS.CO-OPS SOS"
        assert self.c.server.identification.service == 'OGC:SOS'
        assert self.c.server.identification.version == '1.0.0'
        assert self.c.server.identification.abstract == 'NOAA.NOS.CO-OPS Sensor Observation Service (SOS) Server'
        assert self.c.server.identification.keywords == ['Air Temperature', 'Barometric Pressure', 'Conductivity', 'Currents', 'Datum', 'Harmonic Constituents', 'Rain Fall', 'Relative Humidity', 'Salinity', 'Visibility', 'Water Level', 'Water Level Predictions', 'Water Temperature', 'Winds']
        assert self.c.server.identification.fees == 'NONE'
        assert self.c.server.identification.accessconstraints == 'NONE'

    def test_coops_describe_sensor(self):
        self.c.features = ['8454000']
        response = self.c.metadata(output_format='text/xml;subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"')
        assert isinstance(response[0], SensorML)

    def test_raw_coops_get_observation(self):
        self.c.start_time   = datetime.strptime("2012-10-01", "%Y-%m-%d")
        self.c.end_time     = datetime.strptime("2012-10-02", "%Y-%m-%d")
        self.c.features     = ['8454000']
        self.c.variables    = ['http://mmisw.org/ont/cf/parameter/water_surface_height_above_reference_datum']  # noqa

        response = self.c.raw(responseFormat="text/csv")
        assert isinstance(response, basestring)
        """
        station_id,sensor_id,"latitude (degree)","longitude (degree)",date_time,"water_surface_height_above_reference_datum (m)",datum_id,"vertical_position (m)"
        urn:ioos:station:NOAA.NOS.CO-OPS:8454000,urn:ioos:sensor:NOAA.NOS.CO-OPS:8454000:A1,41.8071,-71.4012,2012-10-01T00:00:00Z,1.465,urn:ioos:def:datum:noaa::MLLW,1.064
        """
        data = list(csv.DictReader(StringIO.StringIO(response)))
        assert data[0]['station_id'] == 'urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
        assert data[0]['datum_id'] == "urn:ioos:def:datum:noaa::MLLW"
        assert data[0]['date_time'] == "2012-10-01T00:00:00Z"
        assert data[0]['water_surface_height_above_reference_datum (m)'] == "1.465"
        assert data[0]['vertical_position (m)'] == "1.064"

    def test_raw_coops_get_observation_with_dataType(self):
        self.c.start_time   = datetime.strptime("2012-10-01", "%Y-%m-%d")
        self.c.end_time     = datetime.strptime("2012-10-02", "%Y-%m-%d")
        self.c.features     = ['8454000']
        self.c.variables    = ['http://mmisw.org/ont/cf/parameter/water_surface_height_above_reference_datum']
        self.c.dataType     = "VerifiedHighLow"

        response = self.c.raw(responseFormat="text/csv")
        assert isinstance(response, basestring)
        """
        station_id,sensor_id,"latitude (degree)","longitude (degree)",date_time,"water_surface_height_above_reference_datum (m)",datum_id,"vertical_position (m)"
        urn:ioos:station:NOAA.NOS.CO-OPS:8454000,urn:ioos:sensor:NOAA.NOS.CO-OPS:8454000:W3,41.8071,-71.4012,2012-10-01T01:00:00Z,1.617,urn:ioos:def:datum:noaa::MLLW,1.064
        """
        data = list(csv.DictReader(StringIO.StringIO(response)))
        assert data[0]['station_id'] == 'urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
        assert data[0]['datum_id'] == "urn:ioos:def:datum:noaa::MLLW"
        assert data[0]['date_time'] == "2012-10-01T01:00:00Z"
        assert data[0]['water_surface_height_above_reference_datum (m)'] == "1.617"
        assert data[0]['vertical_position (m)'] == "1.064"

    def test_raw_coops_get_observation_with_datum(self):
        self.c.start_time   = datetime.strptime("2012-10-01", "%Y-%m-%d")
        self.c.end_time     = datetime.strptime("2012-10-02", "%Y-%m-%d")
        self.c.features     = ['8454000']
        self.c.variables    = ['http://mmisw.org/ont/cf/parameter/water_surface_height_above_reference_datum']
        self.c.dataType     = "VerifiedHighLow"
        self.c.datum        = "NAVD"

        response = self.c.raw(responseFormat="text/csv")
        assert isinstance(response, basestring)
        """
        station_id,sensor_id,"latitude (degree)","longitude (degree)",date_time,"water_surface_height_above_reference_datum (m)",datum_id,"vertical_position (m)"
        urn:ioos:station:NOAA.NOS.CO-OPS:8454000,urn:ioos:sensor:NOAA.NOS.CO-OPS:8454000:W3,41.8071,-71.4012,2012-10-01T01:00:00Z,0.863,urn:ogc:def:datum:epsg::5103,1.818
        """
        data = list(csv.DictReader(StringIO.StringIO(response)))
        assert len(data) == 4
        assert data[0]['station_id'] == 'urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
        assert data[0]['datum_id'] == "urn:ogc:def:datum:epsg::5103"
        assert data[0]['date_time'] == "2012-10-01T01:00:00Z"
        assert data[0]['water_surface_height_above_reference_datum (m)'] == "0.863"
        assert data[0]['vertical_position (m)'] == "1.818"
