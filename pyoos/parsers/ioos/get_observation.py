from __future__ import (absolute_import, division, print_function)

from pyoos.utils.etree import ElementType, etree
from owslib.namespaces import Namespaces
from owslib.util import testXMLValue

ns = Namespaces()


class IoosGetObservation(object):
    def __new__(cls, element):
        if isinstance(element, ElementType):
            root = element
        else:
            root = etree.fromstring(element)

        if hasattr(root, 'getroot'):
            root = root.getroot()

        XLINK_NS = ns.get_namespace("xlink")
        GML_NS = [ns.get_versioned_namespace('gml', '3.1.1')]
        version = None
        for g in GML_NS:
            try:
                version = testXMLValue(root.find("{%s}metaDataProperty[@{%s}title='ioosTemplateVersion']/{%s}version" % (g, XLINK_NS, g)))
                break
            except:
                continue

        if version == "1.0":
            from pyoos.parsers.ioos.one.get_observation import GetObservation as GO10
            return super(IoosGetObservation, cls).__new__(GO10)
        else:
            raise ValueError("Unsupported IOOS version {}.  Supported: [1.0]".format(version))

    def __init__(self, element):
        # Get individual om:Observations has a hash or name:ob.
        if isinstance(element, ElementType):
            self._root = element
        else:
            self._root = etree.fromstring(element)

        if hasattr(self._root, 'getroot'):
            self._root = self._root.getroot()

        self.observations = []
