from owslib.util import nspath as nsp
from owslib.util import nspath_eval as nspv
from owslib.util import testXMLAttribute, testXMLValue
from owslib.crs import Crs
import csv
import StringIO

class SweBase(object):
    def __init__(self, **kwargs):
        self.GML_NS = kwargs.pop('GML_NS')
        self.OM_NS = kwargs.pop('OM_NS')
        self.SWE_NS = kwargs.pop('SWE_NS')

        self._foi = kwargs.pop('feature_of_interest')
        self._result = kwargs.pop('result')

        self._location = self._foi.find(nsp("FeatureCollection/location", self.GML_NS))

        self.results = OmResult(self._result, self.SWE_NS)

class OmResult(object):
    """
        An IOOS formatted <om:result> block
    """
    def __init__(self, element, swe_ns):
        self._root = element

        self.fields = []
        self.vector = None
        for field in self._root.findall(nsp("*/field", swe_ns)):
            name = testXMLAttribute(field, "name")
            if name == "location":
                self.vector = SweVector(field.find(nsp("Vector",swe_ns)), swe_ns)
                [self.fields.append(coord) for coord in self.vector.coordinates]
            else:
                self.fields.append(SweField(field, swe_ns))

        encoding = SweEncoding(self._root.find(nsp("*/encoding", swe_ns)), swe_ns)
        self.values = SweValues(self._root.find(nsp("*/values", swe_ns)), encoding)

class SweField(object):
    def __init__(self, element, swe_ns):
        self._root = element

        # Gets whatever the first child is.
        # Could be: Time, Vector, or Quality
        # swe:Time = time
        # swe:Vector = location
        # swe:Quantity = value
        ob = self._root[0]

        self.name = testXMLAttribute(self._root, "name")
        self.definition = testXMLAttribute(ob, "definition")
        self.units = testXMLAttribute(ob.find(nsp("uom", swe_ns)), "code")
        self.unit_url = testXMLAttribute(ob.find(nsp("uom", swe_ns)), nspv("xlink:href"))
        self.value = testXMLValue(ob.find(nsp("swe:value", swe_ns)))
        self.axis = testXMLAttribute(ob, "axisID")

class SweVector(object):
    def __init__(self, element, swe_ns):
        self._root = element

        self.definition = testXMLAttribute(self._root, "definition")
        self.srs = testXMLAttribute(self._root, "referenceFrame")

        self.coordinates = []
        for coord in self._root.findall(nsp("coordinate", swe_ns)):
            self.coordinate.append(SweField(coord), swe_ns)

class SweValues(object):
    """
        We are only supporting block_seperators that are newlines.
    """
    def __init__(self, element, encoding):
        text = StringIO.StringIO(testXMLValue(element))
        reader = csv.reader(text, delimiter=',')
        self.reader = ((r.strip() for r in row) for row in reader)

class SweEncoding(object):
    def __init__(self, element, swe_ns):
        self._root = element

        # Only supporting Text Encoding
        tx = self._root.find(nsp("TextEncoding", swe_ns))
        if tx is not None:
            self.type = "text"
            self.decimal_separator = testXMLAttribute(tx,'decimalSeparator') or "."
            self.token_separator = testXMLAttribute(tx,'tokenSeparator') or ","
            self.block_separator = testXMLAttribute(tx,'blockSeparator') # ignored, we use newlines
        else:
            raise TypeError("Only swe:TextEncoding is supported at this time")