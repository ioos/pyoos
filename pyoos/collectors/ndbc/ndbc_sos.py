from __future__ import (absolute_import, division, print_function)
from six import text_type, string_types

from pyoos.collectors.ioos.swe_sos import IoosSweSos


class NdbcSos(IoosSweSos):
    def __init__(self, **kwargs):
        if kwargs.get("test", None) is True:
            kwargs["url"] = "http://sdftest.ndbc.noaa.gov/sos/server.php"
        else:
            kwargs["url"] = 'http://sdf.ndbc.noaa.gov/sos/server.php'

        super(NdbcSos, self).__init__(**kwargs)
        self._datum = None
        self._dataType = None

    def setup_params(self, **kwargs):
        params = super(NdbcSos, self).setup_params(**kwargs)

        if self.bbox is not None:
            params["featureofinterest"] = "BBOX:%s" % ",".join([text_type(x) for x in self.bbox])

        if self.features is None or len(self.features) < 1:
            params["offerings"] = ["urn:ioos:network:noaa.nws.ndbc:all"]
        elif len(self.features) > 1:
            # TODO: Send many requests, one for each station, rather than a network:all
            print("NDBC does not support filtering by > 1 station at a time... returning all stations.")
            params["offerings"] = ["urn:ioos:network:noaa.nws.ndbc:all"]
        elif len(self.features) == 1:
            params["offerings"] = ["urn:ioos:station:wmo:%s" % self.features[0]]

        if params.get("responseFormat", None) is None:
            params["responseFormat"] = 'text/csv'

        if self.variables is None or len(self.variables) < 1:
            raise ValueError("You must set a filter for at least one variable (observedProperty)")
        else:
            ops = ",".join(self.variables)
            if isinstance(ops, string_types):
                ops = [ops]
            params["observedProperties"] = ops

        return params

    def metadata(self, **kwargs):
        callback = lambda x: "urn:ioos:station:wmo:%s" % x
        return super(NdbcSos, self).metadata(feature_name_callback=callback, **kwargs)
