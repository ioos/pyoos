from __future__ import absolute_import, division, print_function

import unittest

import pytest
from owslib.swe.sensor.sml import SensorML

from pyoos.collectors.ioos.swe_sos import IoosSweSos


class IoosSweSosTest(unittest.TestCase):
    def setUp(self):
        # we have to pick SOS to test against, NANOOS it is:
        self.c = IoosSweSos("http://data.nanoos.org/52nsos/sos/kvp")
        # self.c.features = [urn.name for urn in self.c.server.offerings]

    @pytest.mark.xfail
    def test_server_id(self):
        assert (
            self.c.server.identification.title
            == "NANOOS Sensor Observation Service (SOS), a 52North IOOS SOS server"
        )
        assert self.c.server.identification.service == "OGC:SOS"
        assert self.c.server.identification.version == "1.0.0"
        assert self.c.server.identification.fees == "NONE"
        assert self.c.server.identification.accessconstraints == "NONE"

    @pytest.mark.xfail
    def test_metdata(self):
        self.c.features = ["urn:ioos:station:nanoos:apl_nemo"]
        response = self.c.metadata(
            output_format='text/xml; subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"'
        )
        assert isinstance(response, list)
        assert isinstance(response[0], SensorML)

    @pytest.mark.xfail
    def test_metadata_plus_exceptions(self):
        self.c.features = ["urn:ioos:station:nanoos:apl_nemo"]
        response, failures = self.c.metadata_plus_exceptions(
            output_format='text/xml; subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"'
        )
        assert isinstance(response, dict)
        assert isinstance(failures, dict)
        assert isinstance(response[self.c.features[0]], SensorML)


#    def test_raw_get_observation(self):
#        self.c.start_time   = datetime.strptime("2014-10-23", "%Y-%m-%d")
#        self.c.end_time     = datetime.strptime("2014-10-24", "%Y-%m-%d")
#        self.c.features     = ['urn:ioos:station:nanoos:cmop_saturn08']
#        self.c.variables    = ['sea_water_temperature']

#        response = self.c.raw(responseFormat="text/xml;+subtype=\"om/1.0.0/profiles/ioos_sos/1.0\"").decode()
#        assert isinstance(response, string_types)
