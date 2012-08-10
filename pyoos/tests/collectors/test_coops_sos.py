import unittest
from pyoos.collectors.coops.coops_sos import CoopsSos

class CoopsSosTest(unittest.TestCase):

    def setUp(self):
        self.c = CoopsSos()

    def test_coops_server_id(self):
        assert self.c.server.identification.title == "NOAA.NOS.CO-OPS SOS"
        assert self.c.server.identification.service == 'OGC:SOS'
        assert self.c.server.identification.version == '1.0.0'
        assert self.c.server.identification.abstract == 'NOAA.NOS.CO-OPS Sensor Observation Service (SOS) Server'
        assert self.c.server.identification.keywords == ['Air Temperature', 'Barometric Pressure', 'Conductivity', 'Currents', 'Datums', 'Rain Fall', 'Relative Humidity', 'Harmonic Constituents', 'Salinity', 'Water Level', 'Water Level Predictions', 'Water Temperature', 'Winds']
        assert self.c.server.identification.fees == 'NONE'
        assert self.c.server.identification.accessconstraints == 'NONE'

    def test_coops_describe_sensor(self):
        procedure = self.c.server.offerings[1].procedures[0]
        outputFormat = self.c.server.get_operation_by_name('DescribeSensor').parameters['outputFormat']['values'][0]
        response = self.c.get_metadata(procedure=procedure,
                                       outputFormat=outputFormat)
        assert isinstance(response.systems[0].id, str)

    def test_coops_get_observation(self):
        eventTime = None
        stations = {}
        station_names = set(['station-9052000']) 
        for offering in self.c.server.offerings:
            if offering.id in station_names:
                stations[offering.id] = offering
        station = stations[key]
        response = res = self.c.get_raw_data(
                                   offerings=[station.name],
                                   responseFormat='text/csv',
                                   observedProperties=['http://mmisw.org/ont/cf/parameter/water_surface_height_above_reference_datum'],
                                   eventTime=eventTime,
                                   dataType='VerifiedSixMinute')
        #assert isinstance(response, str)

