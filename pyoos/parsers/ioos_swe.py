from pyoos.utils.etree import etree
from owslib.namespaces import OWSLibNamespaces
from owslib.util import testXMLValue, testXMLAttribute, extract_time
from owslib.util import nspath as nsp
from owslib.util import nspath_eval as nspv
from owslib.crs import Crs
from pyoos.parsers.swe.swe_timeseries import SweTimeSeries
from shapely.geometry import box

ns = OWSLibNamespaces()

class IoosSwe(object):
    def __init__(self, element):
        if isinstance(element, str):
            self._root = etree.fromstring(element)
        else:
            self._root = element

        if hasattr(self._root, 'getroot'):
            self._root = self._root.getroot()

        # Get individual om:Observations
        self.observations = {}
        for ob in self._root.findall(nsp("member/Observation", ns.get_versioned_namespace('om','1.0'))):
            ob_ele = OmObservation(ob)
            self.observations[ob_ele.name] = ob_ele

class OmObservation(object):
    def __init__(self, element):
        self._root = element

        OM_NS = ns.get_versioned_namespace('om','1.0')
        GML_NS = ns.get_versioned_namespace('gml','3.1.1')
        SWE_NS = ns.get_versioned_namespace('swe','1.0')
        
        self.name = testXMLValue(self._root.find(nsp("name", GML_NS)))
        self.description = testXMLValue(self._root.find(nsp("description", GML_NS)))
        self.observedProperties = []
        for op in self._root.findall(nsp('observedProperty', OM_NS)):
            self.observedProperties.append(testXMLAttribute(op,nspv('xlink:href')))

        # BBOX
        try:
            envelope = self._root.find(nsp('boundedBy/Envelope', GML_NS))
            lower_left_corner = testXMLValue(envelope.find(nsp('lowerCorner', GML_NS))).split(" ")
            upper_right_corner = testXMLValue(envelope.find(nsp('upperCorner', GML_NS))).split(" ")

            self.bbox_srs = Crs(testXMLAttribute(envelope,'srsName'))
            # Always keep the BBOX as minx, miny, maxx, maxy
            if self.bbox_srs.axisorder == "yx":
                self.bbox = box(float(lower_left_corner[1]), float(lower_left_corner[0]), float(upper_right_corner[1]), float(upper_right_corner[0]))
            else:
                self.bbox = box(float(lower_left_corner[0]), float(lower_left_corner[1]), float(upper_right_corner[0]), float(upper_right_corner[1]))
        except Exception:
            self.bbox = None
            self.bbox_srs = None

        # Time range
        fp = nsp('samplingTime', OM_NS)
        mp = nsp('TimePeriod', GML_NS)

        lp = nsp('beginPosition', GML_NS)
        begin_position_element = self._root.find('%s/%s/%s' % (fp, mp, lp))
        self.begin_position = extract_time(begin_position_element)

        ep = nsp('endPosition', GML_NS)
        end_position_element = self._root.find('%s/%s/%s' % (fp, mp, ep))
        self.end_position = extract_time(end_position_element)

        feature_of_interest_element = self._root.find(nsp("featureOfInterest", OM_NS))
        self.feature_type = testXMLValue(feature_of_interest_element.find(nsp("FeatureCollection/metaDataProperty/name", GML_NS)))

        # Now the fields change depending on the FeatureType
        result_element = self._root.find(nsp("result", OM_NS))

        #TODO: This should be implemented as a Factory
        self.feature = None
        if self.feature_type == 'timeSeries':
            self.feature = SweTimeSeries(feature_of_interest=feature_of_interest_element, result=result_element, GML_NS=GML_NS, OM_NS=OM_NS, SWE_NS=SWE_NS)
        elif self.feature_type == 'trajectoryProfile':
            self.feature = SweTrajectoryProfile(feature_of_interest=feature_of_interest_element, result=result_element, GML_NS=GML_NS, OM_NS=OM_NS, SWE_NS=SWE_NS)
        elif self.feature_type == 'timeSeriesProfile':
            self.feature = SweTimeseriesProfile(feature_of_interest=feature_of_interest_element, result=result_element, GML_NS=GML_NS, OM_NS=OM_NS, SWE_NS=SWE_NS)
