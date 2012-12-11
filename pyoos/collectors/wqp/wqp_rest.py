from pyoos.collectors.collector import Collector
from pyoos.utils.etree import etree
from pyoos.parsers.wqx.wqx_outbound import WqxOutbound
import requests

class WqpRest(Collector):
    def __init__(self, **kwargs):
        super(WqpRest,self).__init__()
        self.sites_url = kwargs.get('sites_url', "http://www.waterqualitydata.us/Station/search")
        self.results_url = kwargs.get('results_url', "http://www.waterqualitydata.us/Result/search")
        self.characteristics_url = kwargs.get("characteristics_url", "http://www.waterqualitydata.us/Codes/Characteristicname")
        self.characteristic_types_url = kwargs.get("characteristic_types_url", "http://www.waterqualitydata.us/Codes/Characteristictype")

    def get_metadata(self, **kwargs):
        kwargs["mimeType"] = "xml"
        response = self.get_raw_sites_data(**kwargs)
        return WqxOutbound(response)

    def get_data(self, **kwargs):
        kwargs["mimeType"] = "xml"
        response = self.get_raw_results_data(**kwargs)
        return WqxOutbound(response)
        
    def get_characterisic_types(self, **kwargs):
        root = etree.fromstring(requests.get(self.characteristic_types_url).text)
        return (x.get('value') for x in root.findall('Code'))

    def get_characteristics(self, **kwargs):
        root = etree.fromstring(requests.get(self.characteristics_url).text)
        return (x.get('value') for x in root.findall('Code'))

    def get_raw_sites_data(self, **kwargs):
        params = self.setup_params(**kwargs)
        return requests.get(self.sites_url, params=params).text

    def get_raw_results_data(self, **kwargs):
        params = self.setup_params(**kwargs)
        return requests.get(self.results_url, params=params).text

    def setup_params(self, **kwargs):
        params = kwargs
        if self.start_time is not None:
            params["startDateLo"] = self.start_time.strftime("%m/%d/%Y")
        if self.end_time is not None:
            params["startDateHi"] = self.end_time.strftime("%m/%d/%Y")

        params["command.avoid"] = "NWIS"

        return params