from pyoos.collectors.collector import Collector
#from pyoos.utils.etree import etree
from pyoos.parsers.awc import AwcToPaegan
import requests

class AwcRest(Collector):
    def __init__(self, **kwargs):
        super(AwcRest, self).__init__()
        self.stations_url = 'http://weather.noaa.gov/data/nsd_cccc.txt'
        self.data_url     = 'http://www.aviationweather.gov/adds/dataserver_current/httpparam'
        
    def get_stations(self):
        if self._features is None:
            r = requests.get(self.stations_url)
            self._stations = [line.split(';')[0] for line in r.text.split('\n')]
            if self._stations[-1] == '':
                self._stations.pop()
            self._features = self._stations
        return self._features
    def set_stations(self, codes):
        self._features = codes
        self._stations = codes
    stations = property(get_stations, set_stations)

    def list_features(self):
        return self.features
    
    def get_raw_response(self, **kwargs):
        r = requests.get(self.data_url, params=kwargs)
        return r.text
        
    def setup_params(self, **kwargs):
        params = kwargs
        params["minLat"] = ''
        params["minLon"] = ''
        params["maxLat"] = ''
        params["maxLon"] = ''
        if self.bbox is not None: # Must be in format: (minx, miny, maxx, maxy)
            params["minLat"] = self.bbox[1]
            params["minLon"] = self.bbox[0]
            params["maxLat"] = self.bbox[3]
            params["maxLon"] = self.bbox[2]
        #if self.features is not None:
        #    params["siteid"] = self.features[0]
        return params

    def collect(self):
        params = self.setup_params(format="xml", hoursBeforeNow="48", requestType="retrieve", dataSource="metars")
        data = self.get_raw_response(**params)
        return AwcToPaegan(data).feature

    def raw(self, **kwargs):
        params = self.setup_params(format="xml", hoursBeforeNow="48", requestType="retrieve", dataSource="metars")
        data = self.get_raw_response(**params)
        return data
