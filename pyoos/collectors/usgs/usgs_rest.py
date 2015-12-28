from __future__ import (absolute_import, division, print_function)
from six import string_types

from pyoos.collectors.collector import Collector
import requests
from pyoos.parsers.waterml import WaterML11ToPaegan


class UsgsRest(Collector):
    def __init__(self, **kwargs):
        super(UsgsRest, self).__init__()
        self.rest_url = 'http://waterservices.usgs.gov/nwis/iv'
        self._state = None

    def set_state(self, state):
        if state is not None:
            if not isinstance(state, string_types):
                raise ValueError("Not a recognized state. \
                                  Must be a str or unicode string")
        self._state = state

    def get_state(self):
        return self._state
    state = property(get_state, set_state)

    def list_variables(self):
        return "Find variables using this website: http://help.waterdata.usgs.gov/codes-and-parameters/parameters"

    def list_features(self):
        return "Find features using this mapping client: http://maps.waterdata.usgs.gov/mapper/"

    def clear(self):
        super(UsgsRest, self).clear()
        self._state = None

    def setup_params(self, **kwargs):
        params = kwargs

        majors = [_f for _f in [self.bbox, self.features, self.state] if _f]
        if len(majors) > 1:
            raise ValueError("""USGS does not allow filtering by more than one 'major' filter.
                                State, BBox, and Features (sites) are all considered 'major' filters.
                                Please set all but one of the filters to None and try again.""")

        if self.start_time is not None:
            params["startDT"] = self.start_time.strftime('%Y-%m-%dT%H:%M')
        if self.end_time is not None:
            params["endDT"] = self.end_time.strftime('%Y-%m-%dT%H:%M')
        if self.bbox is not None:
            params["bBox"] = ",".join([str(x) for x in self.bbox])
        if self.variables is not None and len(self.variables) > 0:
            params["parameterCd"] = ",".join(self.variables)
        if self.features is not None and len(self.features) > 0:
            params["sites"] = ",".join(self.features)
        if self.state is not None:
            params["stateCd"] = self.state

        # Get WaterML 1.1
        params["format"] = "waterml,1.1"

        return params

    def collect(self):
        params = self.setup_params()
        data = requests.get(self.rest_url, params=params).text
        return WaterML11ToPaegan(data).feature

    def raw(self, **kwargs):
        params = self.setup_params()
        return requests.get(self.rest_url, params=params).text
