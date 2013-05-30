import unittest
from pyoos.collectors.ndbc.ndbc_sos import NdbcSos
from owslib.swe.sensor.sml import SystemMetadata

class NdbcSosTest(unittest.TestCase):

    def setUp(self):
        self.c = NdbcSos()

    def test_ndbc_server_id(self):
        assert self.c.server.identification.title == "National Data Buoy Center SOS"
        assert self.c.server.identification.service == 'OGC:SOS'
        assert self.c.server.identification.version == '1.0.0'
        assert self.c.server.identification.abstract == 'National Data Buoy Center SOS'
        #assert self.c.server.identification.keywords == ['Weather', 'Ocean Currents', 'Air Temperature', 'Water Temperature', 'Conductivity', 'Salinity', 'Barometric Pressure', 'Water Level', 'Waves', 'Winds', 'NDBC']
        assert self.c.server.identification.fees == 'NONE'
        assert self.c.server.identification.accessconstraints == 'NONE'

    def test_ndbc_describe_sensor(self):
        procedure = self.c.server.offerings[1].procedures[0]
        outputFormat = self.c.server.get_operation_by_name('DescribeSensor').parameters['outputFormat']['values'][0]
        response = self.c.get_metadata(procedure=procedure,
                                       outputFormat=outputFormat)

        assert isinstance(response.systems[0], SystemMetadata)

    def test_ndbc_get_observation(self):
        offering = self.c.server.offerings[1]
        # NDBC only allows one offering at a time
        offerings = [offering.name]
        responseFormat = offering.response_formats[0]
        # NDBC only allows one observed_property at a time
        observedProperties = [offering.observed_properties[1]]
        eventTime = None
        response = self.c.get_data(offerings=offerings,
                                   responseFormat=responseFormat,
                                   observedProperties=observedProperties,
                                   eventTime=eventTime)
        #assert isinstance(response, str)
