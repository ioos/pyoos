from pyoos.collectors.collector import Collector
from pyoos.parsers.ioos.describe_sensor import IoosDescribeSensor
from pyoos.parsers.ioos.get_observation import IoosGetObservation
from owslib.sos import SensorObservationService as Sos
from owslib.swe.sensor.sml import SensorML

class IoosSweSos(Collector):
    def __init__(self, url, xml=None):
        super(IoosSweSos,self).__init__()
        self.server = Sos(url, xml=xml)

    def metadata(self, **kwargs):
        callback = kwargs.get("feature_name_callback", None) or str
        kwargs['outputFormat'] = 'text/xml;subtype="sensorML/1.0.1"'

        responses = []
        if self.features is not None:
            for feature in self.features:
                kwargs['procedure'] = callback(feature)
                responses.append(SensorML(self.server.describe_sensor(**kwargs)))

        return responses

    def setup_params(self, **kwargs):
        params = kwargs

        # TODO: BBOX needs to be implemented as an OGC Filter.
        # This page has a good example: http://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/index.jsp
        # Click on "Collection" in the POST example to see what it should look like.
        # Requires changing from GET to POST...
        if self.bbox is not None:
            print "BBOX requests for IOOS SWE SOS services are not yet implemented"

        if self.start_time is not None:
            params["eventTime"] = self.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        if self.end_time is not None:
            params["eventTime"] += "/%s" % self.end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        if self.variables is None or len(self.variables) < 1:
            raise ValueError("You must set a filter for at least one variable (observedProperty)")
        else:
            ops = ",".join(self.variables)
            if isinstance(ops, basestring):
                ops = [ops]
            params["observedProperties"] = ops

        return params

    def collect(self, **kwargs):
        kwargs["responseFormat"] = 'text/xml;subtype="om/1.0.0/profiles/ioos_sos/1.0"'
        return IoosGetObservation(self.raw(**kwargs)).feature

    def raw(self, **kwargs):
        params = self.setup_params(**kwargs)
        return self.server.get_observation(**params)