from __future__ import (absolute_import, division, print_function)
from six import string_types

from pyoos.collectors.collector import Collector
from pyoos.parsers.ioos.get_observation import IoosGetObservation
from owslib.ows import ExceptionReport
from owslib.sos import SensorObservationService as Sos
from owslib.swe.sensor.sml import SensorML
from owslib.util import ServiceException


class IoosSweSos(Collector):
    def __init__(self, url, xml=None):
        super(IoosSweSos, self).__init__()
        self.server = Sos(url, xml=xml)

    def metadata(self, output_format=None, feature_name_callback=None, **kwargs):
        """
        Gets SensorML objects for all procedures in your filtered features.

        You should override the default output_format for servers that do not
        respond properly.
        """
        callback = feature_name_callback or str
        if output_format is None:
            output_format = 'text/xml; subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"'

        responses = []
        if self.features is not None:
            for feature in self.features:
                ds_kwargs = kwargs.copy()
                ds_kwargs.update({'outputFormat': output_format,
                                  'procedure'   : callback(feature)})

                responses.append(SensorML(self.server.describe_sensor(**ds_kwargs)))

        return responses

    def metadata_plus_exceptions(self, output_format=None, feature_name_callback=None, **kwargs):
        """
        Gets SensorML objects for all procedures in your filtered features.

        Return two dictionaries for service responses keyed by 'feature':
            responses: values are SOS DescribeSensor response text
            response_failures: values are exception text content furnished from ServiceException, ExceptionReport

        You should override the default output_format for servers that do not
        respond properly.
        """
        callback = feature_name_callback or str
        if output_format is None:
            output_format = 'text/xml; subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"'

        responses = {}
        response_failures = {}
        if self.features is not None:
            for feature in self.features:
                ds_kwargs = kwargs.copy()
                ds_kwargs.update({'outputFormat': output_format,
                                  'procedure'   : callback(feature)})
                try:
                    responses[feature] = (SensorML(self.server.describe_sensor(**ds_kwargs)))
                except (ServiceException, ExceptionReport) as e:
                    response_failures[feature] = str(e)

        return (responses, response_failures)

    def setup_params(self, **kwargs):
        params = kwargs

        if self.bbox is not None:
            params["featureOfInterest"] = "BBOX:%s,%s,%s,%s" % (self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])

        if self.start_time is not None:
            params["eventTime"] = self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if self.end_time is not None:
            params["eventTime"] += "/%s" % self.end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        if self.variables is None or len(self.variables) < 1:
            raise ValueError("You must set a filter for at least one variable (observedProperty)")
        else:
            ops = ",".join(self.variables)
            if isinstance(ops, string_types):
                ops = [ops]
            params["observedProperties"] = ops

        return params

    def collect(self, **kwargs):
        # there is an unfortunate difference in how 52N and ncSOS handle the response format.
        # 52N expects subtype, ncSOS expects schema.
        # consult the observed properties and getcaps to figure out which should be used if none passed
        if 'responseFormat' not in kwargs:

            # iterate offerings and see if we need to change to subtype
            off_dict = {off.name : off for off in self.server.offerings}

            response_format = None

            for offering in kwargs.get('offerings', []):
                if offering not in off_dict:
                    continue

                ioos_formats = [rf for rf in off_dict[offering].response_formats if 'ioos_sos/1.0' in rf]
                if not len(ioos_formats):
                    raise Exception("No ioos_sos/1.0 response format found for offering {}".format(offering))

                if response_format != ioos_formats[0]:
                    response_format = ioos_formats[0]

            kwargs["responseFormat"] = response_format

        return IoosGetObservation(self.raw(**kwargs)).observations

    def raw(self, **kwargs):
        params = self.setup_params(**kwargs)
        return self.server.get_observation(**params)
