from __future__ import (absolute_import, division, print_function)

import pytz

class Collector(object):

    def __init__(self):
        self._end_time = None
        self._start_time = None
        self._bbox = None
        self._variables = None
        self._features = None

    def get_start_time(self):
        """
            The start time to collect data from
            This should be overwritten by subclasses
        """
        return self._start_time

    def set_start_time(self, time):
        if time is not None:
            if not time.tzinfo:
                time = time.replace(tzinfo=pytz.utc)
            time = time.astimezone(pytz.utc)
        self._start_time = time
    start_time = property(get_start_time, set_start_time)

    def get_end_time(self):
        """
            The end time to collect data to
        """
        return self._end_time

    def set_end_time(self, time):
        if time is not None:
            if not time.tzinfo:
                time = time.replace(tzinfo=pytz.utc)
            time = time.astimezone(pytz.utc)
        self._end_time = time
    end_time = property(get_end_time, set_end_time)

    def get_bbox(self):
        """
            The bbox to collect data from as a (minx, miny, maxx, maxy) tuple
        """
        return self._bbox

    def set_bbox(self, bbox):
        if bbox is not None:
            if isinstance(bbox, list) or isinstance(bbox, tuple):
                bbox = tuple(bbox)
            else:
                raise ValueError("Not a recognized bbox. \
                                  Must be in format: (minx, miny, maxx, maxy)")
        self._bbox = bbox
    bbox = property(get_bbox, set_bbox)

    def get_variables(self):
        """
            The variables to collect data from as a list of strings.
        """
        return self._variables

    def set_variables(self, variables):
        if variables is not None:
            if isinstance(variables, list) or isinstance(variables, tuple):
                variables = list(variables)
            else:
                raise ValueError("Not a recognized variable list. \
                                  Must be a list or tuple of strings")
        self._variables = variables
    variables = property(get_variables, set_variables)

    def get_features(self):
        """
            The unique features to collect data from as a list of strings.
        """
        return self._features

    def set_features(self, features):
        if features is not None:
            if isinstance(features, list) or isinstance(features, tuple):
                features = list(features)
            else:
                raise ValueError("Not a recognized variable list. \
                                  Must be a list or tuple of strings")
        self._features = features
    features = property(get_features, set_features)

    def filter(self, **kwargs):
        if kwargs.get("bbox"):
            self.bbox = kwargs.pop("bbox")

        if kwargs.get("start"):
            self.start_time = kwargs.pop("start")

        if kwargs.get("end"):
            self.end_time = kwargs.pop("end")

        if kwargs.get("variables"):
            self.variables = kwargs.pop("variables")

        if kwargs.get("features"):
            self.features = kwargs.pop("features")

        if len(kwargs) > 0:
            # Apply custom filters that are left
            for k, v in kwargs.items():
                setattr(self, k, v)

        # Return self to enable chaining
        return self

    def clear(self):
        self._end_time = None
        self._start_time = None
        self._bbox = None
        self._variables = None
        self._features = None

    def list_variables(self):
        """
            Lists the available variables for this collector
            This should be overwritten by subclasses!
        """
        raise NotImplementedError

    def list_features(self):
        """
            Lists the available features for this collector
            This should be overwritten by subclasses!
        """
        raise NotImplementedError

    def collect(self):
        """
            Do the actual work and return a Paegan CDM object
            This should be overwritten by subclasses!
        """
        raise NotImplementedError

    def raw(self, format=None):
        """
            Do the actual work and return the raw response object from
            This should be overwritten by subclasses!
        """
        raise NotImplementedError
