from pyoos.collectors.collector import Collector
from owslib.sos import SensorObservationService as Sos

class NdbcSos(Collector):
    def __init__(self, **kwargs):
        super(NdbcSos,self).__init__()
        if kwargs.get('test') is True:
            url = 'http://sdftest.ndbc.noaa.gov/sos/server.php'
        else:
            url = 'http://sdf.ndbc.noaa.gov/sos/server.php'

        self.server = Sos(url)

    def get_data(**kwargs):
        True

    def get_describe_sensor_output_formats(self):
    	return self.server.get_operation_by_name('DescribeSensor').parameters['outputFormat']['values']