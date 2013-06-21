from pyoos.utils.etree import etree
from owslib.namespaces import Namespaces
from owslib.util import testXMLValue, testXMLAttribute, extract_time
from owslib.util import nspath as nsp
from owslib.util import nspath_eval
from owslib.crs import Crs
from pyoos.parsers.swe.swe_timeseries import SweTimeSeries
from shapely.geometry import box, Point

from pyoos.parsers.ioos.get_observation import IoosGetObservation

def get_namespaces():
    ns = Namespaces()
    return ns.get_namespaces(["om10", "swe10", "swe20", "gml311", "xlink"])
namespaces = get_namespaces()

def nspv(path):
    return nspath_eval(path, namespaces)

class IoosGetObservation_1_0(IoosGetObservation):
    def __init__(self, element):
        super(IoosGetObservation_1_0, self).__init__(element=element)

        self.ioos_version = "1.0"

        for ob in self._root.findall(nspv("member/Observation", namespaces)):
            ob_ele = OmObservation(ob)
            self.observations.append(ob_ele)


class OmObservation(object):
    def __init__(self, element):
        self._root = element

        self.description = testXMLValue(self._root.find(nspv("gml311:description")))

        self.begin_position = extract_time(self._root.find(nspv('om10:samplingTime/gml311:TimePeriod/gml311:beginPosition')))

        self.end_position = extract_time(self._root.find(nspv('om10:samplingTime/gml311:TimePeriod/gml311:endPosition')))

        self.procedures = [testXMLAttribute(e, nspv("xlink:href")) for e in self._root.findall(nspv("om10:procedure/om10:Process/gml311:member"))]

        self.observedProperties = [testXMLAttribute(e, nspv("xlink:href")) for e in self._root.findall(nspv("om10:observedProperty/swe10:CompositePhenomenon/swe10:component"))]

        self.feature_type = textXMLValue(self._root.find(nspv("om10:featureOfInterest/gml311:FeatureCollection/gml311:metaDataProperty/gml311:name[codeSpace='http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#discrete-sampling-geometries']")))

        # BBOX
        envelope = self._root.find(nspv("om10:featureOfInterest/gml311:FeatureCollection/gml311:boundedBy/gml311:Envelope"))
        self.bbox_srs = Crs(testXMLAttribute(envelope,'srsName'))
        lower_left_corner = testXMLValue(envelope.find(nspv('gml311:lowerCorner'))).split(" ")
        upper_right_corner = testXMLValue(envelope.find(nsp('gml311:upperCorner'))).split(" ")
        if self.bbox_srs.axisorder == "yx":
            self.bbox = box(float(lower_left_corner[1]), float(lower_left_corner[0]), float(upper_right_corner[1]), float(upper_right_corner[0]))
        else:
            self.bbox = box(float(lower_left_corner[0]), float(lower_left_corner[1]), float(upper_right_corner[0]), float(upper_right_corner[1]))
    

        # LOCATION
        location = self._root.find(nspv("om10:featureOfInterest/gml311:FeatureCollection/gml311:location"))
        # Should only have one child
        geo = list(location)[0]
        self.location = {}

        def get_point(element, srs):
            name  = testXMLValue(element.find(nspv("gml311:name")))
            point = textXMLValue(element.find(nspv("gml311:pos"))).split(" ")
            if srs.axisorder == "yx":
                point = Point(point[1], point[0])
            else:
                point = Point(point[0], point[1])
            return name, point

        self.location_srs = Crs(testXMLAttribute(geo, "srsName"))
        if geo.tag == nspv("gml311:Point"):
            n, p = get_point(geo, self.location_srs)
            self.location[n] = p
        elif geo.tag == nspv("gml311:MultiPoint"):
            for point in geo.findall(nspv("gml311:pointMembers/gml311:Point")):
                n, p = get_point(point, self.location_srs)
                self.location[n] = p


        # Now the fields change depending on the FeatureType
        self.results = self._root.find(nspv("om10:result"))

        #TODO: This should be implemented as a Factory
        self.feature = None
        if self.feature_type == 'timeSeries':
            self.feature = SweTimeSeries(feature_of_interest=feature_of_interest_element, result=result_element, GML_NS=GML_NS, OM_NS=OM_NS, SWE_NS=SWE_NS)
        elif self.feature_type == 'timeSeriesProfile':
            self.feature = SweTimeseriesProfile(feature_of_interest=feature_of_interest_element, result=result_element, GML_NS=GML_NS, OM_NS=OM_NS, SWE_NS=SWE_NS)
