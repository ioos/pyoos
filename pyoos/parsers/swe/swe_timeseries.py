from pyoos.parsers.swe.swe_base import SweBase
from pyoos.cdm.features.point import Point
from owslib.util import nspath as nsp
from owslib.util import testXMLAttribute, testXMLValue
from shapely.geometry import Point as sPoint
from owslib.crs import Crs

class SweTimeSeries(SweBase):
    def __init__(self, **kwargs):
        super(SweTimeSeries,self).__init__(**kwargs)

        # Parse out GML point.  Defaults to 0 depth if none specified
        self.geo_srs = Crs(testXMLAttribute(self._location.find(nsp("Point", self.GML_NS)), 'srsName'))
        geo = [float(v) for v in testXMLValue(self._location.find(nsp("Point/pos", self.GML_NS))).split(" ")]

        if self.geo_srs.axisorder == "yx":
            self.geo = sPoint(geo[1], geo[0])
        else:
            self.geo = sPoint(geo[0], geo[1])

        try:
            self.geo.z = geo[2]
        except:
            pass
