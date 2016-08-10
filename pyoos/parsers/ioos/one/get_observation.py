from __future__ import (absolute_import, division, print_function)

from owslib.namespaces import Namespaces
from owslib.util import testXMLValue, testXMLAttribute, extract_time
from owslib.util import nspath_eval
from owslib.crs import Crs

from shapely.geometry import box, Point

from pyoos.parsers.ioos.get_observation import IoosGetObservation
from pyoos.parsers.ioos.one.timeseries import TimeSeries
from pyoos.parsers.ioos.one.timeseries_profile import TimeSeriesProfile


def get_namespaces():
    ns = Namespaces()
    return ns.get_namespaces(["om10", "swe101", "swe20", "gml311", "xlink"])
namespaces = get_namespaces()


def nspv(path):
    return nspath_eval(path, namespaces)


class GetObservation(IoosGetObservation):
    def __init__(self, element):
        super(GetObservation, self).__init__(element=element)

        self.ioos_version = "1.0"

        for ob in self._root.findall(nspv("om10:member/om10:Observation")):
            ob_ele = OmObservation(ob)
            self.observations.append(ob_ele)


class OmObservation(object):
    def __init__(self, element):
        self._root = element

        self.description = testXMLValue(self._root.find(nspv("gml311:description")))

        self.begin_position = extract_time(self._root.find(nspv('om10:samplingTime/gml311:TimePeriod/gml311:beginPosition')))

        self.end_position = extract_time(self._root.find(nspv('om10:samplingTime/gml311:TimePeriod/gml311:endPosition')))

        self.procedures = [testXMLAttribute(e, nspv("xlink:href")) for e in self._root.findall(nspv("om10:procedure/om10:Process/gml311:member"))]

        self.observedProperties = [testXMLAttribute(e, nspv("xlink:href")) for e in self._root.findall(nspv("om10:observedProperty/swe101:CompositePhenomenon/swe101:component"))]

        # Can't use a full Xpath expression, so iterate over all metaDataProperties to find the IOOS FeatureType
        self.feature_type = None
        ft = self._root.findall(nspv("om10:featureOfInterest/gml311:FeatureCollection/gml311:metaDataProperty/gml311:GenericMetaData/gml311:name"))
        ft.extend(self._root.findall(nspv("om10:featureOfInterest/gml311:FeatureCollection/gml311:metaDataProperty/gml311:name")))
        ft_def = "http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#discrete-sampling-geometries"
        for f in ft:
            if testXMLAttribute(f, "codeSpace") == ft_def:
                self.feature_type = testXMLValue(f)

        # BBOX
        envelope = self._root.find(nspv("om10:featureOfInterest/gml311:FeatureCollection/gml311:boundedBy/gml311:Envelope"))
        self.bbox_srs = Crs(testXMLAttribute(envelope, 'srsName'))
        lower_left_corner = testXMLValue(envelope.find(nspv('gml311:lowerCorner'))).split(" ")
        upper_right_corner = testXMLValue(envelope.find(nspv('gml311:upperCorner'))).split(" ")
        if self.bbox_srs.axisorder == "yx":
            self.bbox = box(float(lower_left_corner[1]), float(lower_left_corner[0]), float(upper_right_corner[1]), float(upper_right_corner[0]))
        else:
            self.bbox = box(float(lower_left_corner[0]), float(lower_left_corner[1]), float(upper_right_corner[0]), float(upper_right_corner[1]))

        # LOCATION
        location = self._root.find(nspv("om10:featureOfInterest/gml311:FeatureCollection/gml311:location"))
        # Should only have one child
        geo = list(location)[-1]
        self.location = {}

        def get_point(element, srs):
            name  = testXMLValue(element.find(nspv("gml311:name")))
            point = testXMLValue(element.find(nspv("gml311:pos"))).split(" ")
            if srs.axisorder == "yx":
                point = Point(float(point[1]), float(point[0]))
            else:
                point = Point(float(point[0]), float(point[1]))
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

        # TODO: This should be implemented as a Factory
        self.feature = None
        data = self.results.find(nspv("swe20:DataRecord"))
        if data is not None:
            if self.feature_type == 'timeSeries':
                self.feature = TimeSeries(data).feature
            elif self.feature_type == 'timeSeriesProfile':
                self.feature = TimeSeriesProfile(data).feature
            else:
                print("No feature type found.")
