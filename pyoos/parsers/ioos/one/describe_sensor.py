from __future__ import (absolute_import, division, print_function)
from six import text_type

import itertools

from owslib.swe.sensor.sml import SensorML
from owslib.namespaces import Namespaces
from owslib.util import testXMLValue, testXMLAttribute, nspath_eval

from pyoos.parsers.ioos.describe_sensor import IoosDescribeSensor

from dateutil import parser
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
from pyoos.utils import ElementType, etree
import warnings


def get_namespaces():
    n = Namespaces()
    return n.get_namespaces(["sml101", "gml", "xlink", "swe101"])

namespaces = get_namespaces()
SWE_NS = namespaces['swe101']
SML_NS = namespaces['sml101']
ont = 'http://mmisw.org/ont/ioos/definition/'


def nsp(path):
    return nspath_eval(path, namespaces)


class DescribeSensor(IoosDescribeSensor):
    @classmethod
    def get_named_by_definition(cls, element_list, string_def):
        """Attempts to get an IOOS definition from a list of xml elements"""
        try:
            return next((st.value for st in element_list
                        if st.definition == string_def))
        except:
            return None

    def get_ioos_def(self, ident, elem_type, ont):
        """Gets a definition given an identifier and where to search for it"""
        if elem_type == 'identifier':
            getter_fn = self.system.get_identifiers_by_name
        elif elem_type == 'classifier':
            getter_fn = self.system.get_classifiers_by_name
        else:
            raise ValueError("Unknown element type '{}'".format(elem_type))
        return DescribeSensor.get_named_by_definition(getter_fn(ident),
                                                      urljoin(ont, ident))

    def __init__(self, element):
        """ Common things between all describe sensor requests """
        if isinstance(element, ElementType):
            root = element
        else:
            root = etree.fromstring(element)

        sml_str = ".//{{{0}}}identifier/{{{0}}}Term[@definition='http://mmisw.org/ont/ioos/definition/%s']".format(SML_NS)

        # TODO: make this cleaner
        if hasattr(root, 'getroot'):
            root = root.getroot()
        self.system = SensorML(element).members[0]

        self.ioos_version = testXMLValue(root.find(".//{%s}field[@name='ioosTemplateVersion']/{%s}Text/{%s}value" % (SWE_NS, SWE_NS, SWE_NS)))
        if self.ioos_version != "1.0":
            warnings.warn("Warning: Unsupported IOOS version (%s). Supported: [1.0]" % self.ioos_version)

        self.shortName = self.get_ioos_def('shortName', 'identifier', ont)
        self.longName = self.get_ioos_def('longName', 'identifier', ont)
        self.keywords = list(map(str, self.system.keywords))

        # Location
        try:
            self.location = self.system.location[0]
        except (TypeError, IndexError):  # No location exists
            self.location = None

        # Timerange
        try:
            timerange      = testXMLValue(self.system.get_capabilities_by_name("observationTimeRange")[0].find(".//" + nsp("swe101:TimeRange/swe101:value"))).split(" ")
            self.starting  = parser.parse(timerange[0])
            self.ending    = parser.parse(timerange[1])
        except (AttributeError, TypeError, ValueError, IndexError):
            self.starting  = None
            self.ending    = None

class GenericSensor(DescribeSensor):
    """A class used primarily for extracting data from non-IOOS SWE datasets"""
    def __init__(self, element):
        super(GenericSensor, self).__init__(element=element)
        # try to find an identifier element of some sort
        self.id = None
        for ident in ['sensorId', 'stationId', 'networkId',
                      'Sensor ID', 'Station ID', 'network ID']:
            res = self.system.get_identifiers_by_name(ident)
            if res:
                self.id = res[0].value
                break
        self.variables = [comp.values()[0] for
                          comp in self.system.components]

class NetworkDS(DescribeSensor):
    def __init__(self, element):
        super(NetworkDS, self).__init__(element=element)

        self.id = self.get_ioos_def("networkID", "identifier", ont)

        # Verbose method of describing members.  Pull out each individual procedure
        # there is no 'lower-case' function in XPath 1, so we have to settle
        # with this
        sml_str = ".//{{{0}}}identifier/{{{0}}}Term[@definition='http://mmisw.org/ont/ioos/definition/%s']".format(SML_NS)
        name_trans = """translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"""
        stat_id_val = ".//sml101:identifier[{}='stationid']/sml101:Term/sml101:value".format(name_trans)
        # TODO: maybe refactor to use ioos_get_def instead
        def first_xpath_or_none(e):
            res = e.xpath(stat_id_val, namespaces=namespaces)
            if res:
                return res[0]
            else:
                return None
        self.procedures = sorted(list(set(
                            [testXMLValue(first_xpath_or_none(comp))
                            for comp in self.system.components])))


class StationDS(DescribeSensor):
    def __init__(self, element):
        super(StationDS, self).__init__(element=element)

        self.id = self.get_ioos_def("stationID", "identifier", ont)
        self.platformType = self.get_ioos_def("platformType", "classifier", ont)
        # Verbose method of describing members.  Pull out each individual
        # variable definition
        self.variables = sorted(list(set(
                                 itertools.chain.from_iterable(
                                     [[testXMLAttribute(quan, "definition")
                                      for quan in
                                     comp.findall(".//" +
                                                  nsp("swe101:Quantity"))]
                                      for comp in self.system.components]))))
        # if no variables were picked up, fall back to using original SML
        # components instead
        if not self.variables:
            self.variables = sorted([comp.values()[0] for
                                    comp in self.system.components])


class SensorDS(DescribeSensor):
    def __init__(self, element):
        super(SensorDS, self).__init__(element=element)

        self.id = self.get_ioos_def("sensorID", "identifier", ont)
        self.platformType = self.get_ioos_def("platformType", "classifier", ont)
