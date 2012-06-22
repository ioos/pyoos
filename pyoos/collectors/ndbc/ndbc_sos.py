from pyoos.collectors.collector import Collector
from pyoos.parsers.ioos_describe_sensor import IoosDescribeSensor
from pyoos.parsers.ioos_swe import IoosSwe
from owslib.sos import SensorObservationService as Sos

class NdbcSos(Collector):
    def __init__(self, **kwargs):
        super(NdbcSos,self).__init__()
        if kwargs.get('test') is True:
            url = 'http://sdftest.ndbc.noaa.gov/sos/server.php'
        else:
            url = 'http://sdf.ndbc.noaa.gov/sos/server.php'

        self.server = Sos(url)

    def get_metadata(self, **kwargs):
        response = self.server.describe_sensor(**kwargs)
        return IoosDescribeSensor(response)

    def get_describe_sensor_output_formats(self):
        return self.server.get_operation_by_name('DescribeSensor').parameters['outputFormat']['values']

    def get_data(self, **kwargs):
        response = self.get_raw_data(**kwargs)
        return IoosSwe(response)
        
    def get_raw_data(self, **kwargs):
        return self.server.get_observation(**kwargs)