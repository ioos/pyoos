from __future__ import (absolute_import, division, print_function)

from pyoos.collectors.ioos.swe_sos import IoosSweSos


class CoopsSos(IoosSweSos):
    def __init__(self, **kwargs):
        kwargs["url"] = 'https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS'
        super(CoopsSos, self).__init__(**kwargs)
        self._datum = None
        self._dataType = None

    def set_datatype(self, datatype):
        self._dataType = datatype

    def get_datatype(self):
        return self._dataType
    dataType = property(get_datatype, set_datatype)

    def set_datum(self, datum):
        self._datum = datum

    def get_datum(self):
        return self._datum
    datum = property(get_datum, set_datum)

    def list_datatypes(self):
        # TODO: Get from GetCaps
        return ["PreliminarySixMinute",
                "PreliminaryOneMinute",
                "VerifiedSixMinute",
                "VerifiedHourlyHeight",
                "VerifiedHighLow",
                "VerifiedDailyMean",
                "SixMinuteTidePredictions",
                "HourlyTidePredictions",
                "HighLowTidePredictions"]

    def list_datums(self):
        # TODO: Get from GetCaps
        return ["MLLW",
                "MSL",
                "MHW",
                "STND",
                "IGLD",
                "NAVD"]

    def setup_params(self, **kwargs):
        params = super(CoopsSos, self).setup_params(**kwargs)

        if self.features is None or len(self.features) != 1:
            params["offerings"] = ["urn:ioos:network:NOAA.NOS.CO-OPS:All"]
        elif len(self.features) == 1:
            params["offerings"] = ["urn:ioos:station:NOAA.NOS.CO-OPS:%s" % self.features[0]]

        if self.datum is not None:
            if self.datum in self.list_datums():
                if self.datum == "NAVD":
                    params["result"] = "VerticalDatum==urn:ogc:def:datum:epsg::5103"
                else:
                    params["result"] = "VerticalDatum==urn:ioos:def:datum:noaa::%s" % self.datum
            else:
                raise ValueError("Not a supported datum.  Use list_datums() for options")

        if self.dataType is not None:
            if self.dataType in self.list_datatypes():
                params["dataType"] = self.dataType
            else:
                raise ValueError("Not a supported data type.  Use list_datatypes() for options")

        if params.get("responseFormat", None) is None:
            params["responseFormat"] = 'text/csv'

        return params

    def metadata(self, **kwargs):
        callback = lambda x: "urn:ioos:station:NOAA.NOS.CO-OPS:%s" % x
        return super(CoopsSos, self).metadata(feature_name_callback=callback, **kwargs)
