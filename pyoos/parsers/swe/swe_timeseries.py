from pyoos.parsers.swe.swe_base import SweBase
from pyoos.cdm.features.point import Point
from owslib.util import nspath as nsp
from owslib.util import testXMLAttribute, testXMLValue
from shapely.geometry import Point as sPoint
from owslib.crs import Crs
import dateutil.parser
from pyoos.cdm.utils.member import Member
from pyoos.cdm.collections.point_collection import PointCollection

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


        pc = PointCollection()

        for row in self.results.data:
            p = Point()

            time = None
            z = None
            lat = None
            lon = None

            for field in row:

                if field.axis == "time":
                    t = dateutil.parser.parse(field.value)
                    p.time = t.astimezone(dateutil.tz.tzutc())
                elif field.axis == "Long":
                    lon = field
                elif field.axis == "Lat":
                    lat = field
                elif field.axis == "h":
                    z = field
                else:
                    m = Member(value=field.value,
                               unit=field.units,
                               units_definition=field.units_url,
                               name=field.name,
                               definition=field.definition,
                               standard=field.definition)
                    p.add_member(m)

            # Set the spatial point
            if lon.srs != lat.srs:
                raise ValueError("Longitude and Latitude need to have the same SRS/CRS!")
            p.location = sPoint(float(lon.value), float(lat.value), float(z.value))
            pc.add_element(p)


        self.data = pc