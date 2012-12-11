class SweBase(object):
    def __init__(self, **kwargs):
        self.GML_NS = kwargs.pop('GML_NS')
        self.OM_NS = kwargs.pop('OM_NS')
        self.SWE_NS = kwargs.pop('SWE_NS')

        self._foi = kwargs.pop('feature_of_interest')
        self._result = kwargs.pop('result')

        self._location = self._foi.find(nsp("FeatureCollection/location", self.GML_NS))

        self.results = OmResult(self._result, self.SWE_NS)
