import unittest
from pyoos.collectors.ndbc_sos import NdbcSos

class NdbcSosTest(unittest.TestCase):

    def setUp(self):
        self.c = NdbcSos()

    def test_ndbc_server_id(self):
        assert self.c.server.identification.title == "National Data Buoy Center SOS"
        assert self.c.server.identification.service == 'OGC:SOS'
        assert self.c.server.identification.version == '1.0.0'
        assert self.c.server.identification.abstract == 'National Data Buoy Center SOS'
        assert self.c.server.identification.keywords == ['Weather', 'Ocean Currents', 'Air Temperature', 'Water Temperature', 'Conductivity', 'Salinity', 'Barometric Pressure', 'Water Level', 'Waves', 'Winds', 'NDBC']
        assert self.c.server.identification.fees == 'NONE'
        assert self.c.server.identification.accessconstraints == 'NONE'

    def test_ndbc_describe_sensor(self):
        procedure = self.c.server.offerings[1].procedures[0]
        outputFormat = self.c.server.get_operation_by_name('DescribeSensor').parameters['outputFormat']['values'][0]
        response = self.c.server.describe_sensor(procedure=procedure,
                                                        outputFormat=outputFormat)
        assert isinstance(response, str)

    def test_ndbc_get_observation(self):
        offering = self.c.server.offerings[1]
        offerings = [offering.name]
        responseFormat = offering.response_formats[0]
        observedProperties = [offering.observed_properties[0]]
        eventTime = None
        response = self.c.server.get_observation(offerings=offerings, responseFormat=responseFormat, observedProperties=observedProperties, eventTime=eventTime)

        assert isinstance(response, str)

