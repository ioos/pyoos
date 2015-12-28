from __future__ import (absolute_import, division, print_function)

from pyoos.collectors.collector import Collector
from pyoos.utils.etree import etree
from pyoos.parsers.wqx.wqx_outbound import WqxToPaegan
import requests

class WqpRest(Collector):
    def __init__(self, **kwargs):
        super(WqpRest,self).__init__()
        self.sites_url = kwargs.get('sites_url', "http://www.waterqualitydata.us/Station/search")
        self.results_url = kwargs.get('results_url', "http://www.waterqualitydata.us/Result/search")
        self.characteristics_url = kwargs.get("characteristics_url", "http://www.waterqualitydata.us/Codes/Characteristicname")
        self.characteristic_types_url = kwargs.get("characteristic_types_url", "http://www.waterqualitydata.us/Codes/Characteristictype")

    def get_characterisic_types(self, **kwargs):
        root = etree.fromstring(requests.get(self.characteristic_types_url).text)
        return (x.get('value') for x in root.findall('Code'))

    def get_raw_sites_data(self, **kwargs):
        params = self.setup_params(**kwargs)
        return requests.get(self.sites_url, params=params).text

    def get_raw_results_data(self, **kwargs):
        params = self.setup_params(**kwargs)
        return requests.get(self.results_url, params=params).text

    def set_features(self, features):
        super(WqpRest,self).set_features(features)
        if self._features is not None and len(self._features) > 1:
            raise ValueError("WQP only supports extracting one feature at a time \
                              Please reduce your list to a length of one and try again")
    def get_features(self):
        return self._features
    features = property(get_features, set_features)

    def list_variables(self):
        root = etree.fromstring(requests.get(self.characteristics_url).text)
        return (x.get('value') for x in root.findall('Code'))

    def list_features(self):
        raise NotImplementedError("WQP does not allow returning a list of unique features.")

    def setup_params(self, **kwargs):
        params = kwargs
        if self.start_time is not None:
            params["startDateLo"] = self.start_time.strftime("%m-%d-%Y")
        if self.end_time is not None:
            params["startDateHi"] = self.end_time.strftime("%m-%d-%Y")
        if self.bbox is not None:
            params["bbox"] = ",".join([str(x) for x in self.bbox])
        if self.variables is not None:
            params["characteristicName"] = ";".join(self.variables)
        if self.features is not None:
            params["siteid"] = self.features[0]

        return params

    def collect(self):
        params = self.setup_params(mimeType="xml")
        meta = self.get_raw_sites_data(**params)
        data = self.get_raw_results_data(**params)
        return WqxToPaegan(meta,data).feature

    def raw(self, **kwargs):
        params = self.setup_params(mimeType="xml")
        meta = self.get_raw_sites_data(**params)
        data = self.get_raw_results_data(**params)
        return meta, data

