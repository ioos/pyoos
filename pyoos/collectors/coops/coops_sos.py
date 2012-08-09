from pyoos.collectors.collector import Collector
from pyoos.parsers.ioos_describe_sensor import IoosDescribeSensor
from owslib.sos import SensorObservationService as Sos

class CoopsSos(Collector):
    def __init__(self, **kwargs):
        super(CoopsSos,self).__init__()
        url = 'http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS'

        self.server = Sos(url)

    def get_metadata(self, **kwargs):
        response = self.server.describe_sensor(**kwargs)
        return IoosDescribeSensor(response)

    def get_describe_sensor_output_formats(self):
        return self.server.get_operation_by_name('DescribeSensor').parameters['outputFormat']['values']

    #def get_data(self, **kwargs):
    #    response = self.get_raw_data(**kwargs)
    #    return IoosDif(response)
        
    def get_raw_data(self, **kwargs):
        res = self.server.get_observation(**kwargs)
        if res[41:56] == "ExceptionReport":
            res = -1
        return res
