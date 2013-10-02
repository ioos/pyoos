import itertools

from owslib.swe.sensor.sml import SensorML
from owslib.namespaces import Namespaces
from owslib.util import testXMLValue, testXMLAttribute, nspath_eval

from pyoos.utils.etree import etree
from pyoos.parsers.ioos.describe_sensor import IoosDescribeSensor

from dateutil import parser

def get_namespaces():
    n = Namespaces()
    return n.get_namespaces(["sml101","gml","xlink","swe101"])
namespaces = get_namespaces()

def nsp(path):
    return nspath_eval(path, namespaces)

def get_named_by_definition(element_list, string_def):
    try:
        return next((st.value for st in element_list if st.definition == string_def))
    except:
        return None

class DescribeSensor(IoosDescribeSensor):
    def __init__(self, element):
        super(DescribeSensor, self).__init__(element=element)

        """ Common things between all describe sensor requests """
        self.ioos_version = "1.0"
        self.system = SensorML(element).members[0]

        self.shortName = get_named_by_definition(self.system.get_identifiers_by_name("shortName"), "http://mmisw.org/ont/ioos/definition/shortName")
        self.longName  = get_named_by_definition(self.system.get_identifiers_by_name("longName"), "http://mmisw.org/ont/ioos/definition/longName")
        self.keywords  = map(unicode, self.system.keywords)

        # Location
        try:
            self.location = self.system.location[0]
        except TypeError: # No location exists
            self.location = None

        # Timerange
        try:
            timerange      = testXMLValue(self.system.get_capabilities_by_name("observationTimeRange")[0].find(".//" + nsp("swe101:TimeRange/swe101:value"))).split(" ")
            self.starting  = parser.parse(timerange[0])
            self.ending    = parser.parse(timerange[1])
        except (AttributeError, TypeError, ValueError):
            self.starting  = None
            self.ending    = None

class NetworkDS(DescribeSensor):
    def __init__(self, element):
        super(NetworkDS, self).__init__(element=element)

        self.id             = get_named_by_definition(self.system.get_identifiers_by_name("networkID"), "http://mmisw.org/ont/ioos/definition/networkID")

        # Individual procedures
        self.procedures     = []
        try:
            # Using xlink:href to point to individual member procedures
            self.procedures = sorted(list(set([unicode(testXMLAttribute(comp, nsp("xlink:title")).split(":")[-1]) for comp in self.system.components])))
        except AttributeError:
            # Verbose method of describing members.  Pull out each individual procedure
            self.procedures = sorted(list(set([unicode(testXMLValue(comp.find(".//" + nsp("sml101:identifier[@name='stationID']/sml101:Term/sml101:value")))) for comp in self.system.components])))

class StationDS(DescribeSensor):
    def __init__(self, element):
        super(StationDS, self).__init__(element=element)

        self.id            = get_named_by_definition(self.system.get_identifiers_by_name("stationID"), "http://mmisw.org/ont/ioos/definition/stationID")
        self.platformType  = get_named_by_definition(self.system.get_classifiers_by_name("platformType"), "http://mmisw.org/ont/ioos/definition/platformType")

        # Variables
        self.variables     = []
        try:
            # Using xlink:href to point to individual member sensors
            self.variables = sorted(list(set([unicode(testXMLAttribute(comp, nsp("xlink:title")).split(":")[-1]) for comp in self.system.components])))
        except AttributeError:
            # Verbose method of describing members.  Pull out each individual variable definition
            self.variables = sorted(list(set(itertools.chain.from_iterable([[testXMLAttribute(quan, "definition") for quan in comp.findall(".//" + nsp("swe101:Quantity"))] for comp in self.system.components]))))

class SensorDS(DescribeSensor):
    def __init__(self, element):
        super(SensorDS, self).__init__(element=element)

        self.id = get_named_by_definition(self.system.get_identifiers_by_name("sensorID"), "http://mmisw.org/ont/ioos/definition/sensorID")
