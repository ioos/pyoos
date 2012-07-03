from owslib.util import nspath as nsp
from owslib.util import nspath_eval as nspv
from owslib.util import testXMLAttribute, testXMLValue
from owslib.crs import Crs
import csv
import StringIO
import copy

def get_field_object(element, swe_ns):

    field_tag = nsp("field", swe_ns)
    data_choice_tag = nsp("DataChoice", swe_ns)

    if element.tag == field_tag:
        name = testXMLAttribute(element, "name")
        if name == "location":
            return SweVector(element.find(nsp("Vector", swe_ns)), swe_ns)
        elif name == "time":
            return SweTime(element.find(nsp("Time", swe_ns)), swe_ns)
        else:
            return SweField(element, swe_ns)
    elif element.tag == data_choice_tag:
        return SweDataChoice(element, swe_ns)
    else:
        return None

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
        self.swe_ns = swe_ns
        self.fields = []

        encoding = SweEncoding(self._root.find(nsp("*/encoding", self.swe_ns)), self.swe_ns)
        csv = SweValues(self._root.find(nsp("*/values", self.swe_ns)), encoding).csv
        self.data = self.parse_fields_and_csv(csv)

        for child in self._root.find(nsp("DataStream", self.swe_ns)):
            # Create an array of possible columns
            x = get_field_object(child, self.swe_ns)
            if x is not None:
                self.fields.append(x)

    def parse_fields_and_csv(self, csv):
        """
            Parse CSV and Metadata into an generator of SweFields
        """
        return (self.parse_row(list(row)) for row in csv)

    def parse_row(self, row_data):
        """
            Returns an array of SweFields with their "value" attibute present.
            The value attribute is taken from the default value for that column,
            or from the actual CSV data.
        """
        full = []
        i = 0
        for field in self.fields:
            query_row = row_data[i]
            if isinstance(field, SweDataChoice):
                i += 1
            for f in self.flatten_field(field, query_row):
                try:
                    data = row_data[i]
                except IndexError:
                    data = None
                newfield, increment = self.enhance_field(f, data)
                full.append(newfield)
                if increment is True:
                    i += 1
        return full

    def flatten_field(self, x, query):
        """
            Returns Generator of non-iterable SweFields
        """
        if isinstance(x, SweField):
            yield x
        else:
            for y in x.get_fields(choice=query):
                for k in self.flatten_field(y, query):
                    yield k

    def enhance_field(self, field, value_from_row):
        new_f = copy.copy(field)
        if new_f.value is not None:
            # A constant value is set for this field
            return new_f, False
        else:
            # Pull the value for the row_data
            new_f.value = value_from_row
            return new_f, True


class SweField(object):
    def __init__(self, element, swe_ns):
        self._root = element

        # Gets whatever the first child is.
        # swe:Quantity = value
        ob = self._root[0]

        self.name = testXMLAttribute(self._root, "name")
        self.definition = testXMLAttribute(ob, "definition")
        self.units = testXMLAttribute(ob.find(nsp("uom", swe_ns)), "code")
        self.units_url = testXMLAttribute(ob.find(nsp("uom", swe_ns)), nspv("xlink:href"))
        self.value = testXMLValue(ob.find(nsp("value", swe_ns)))
        self.axis = testXMLAttribute(ob, "axisID")

class SweCoordinate(SweField):
    def __init__(self, element, swe_ns, srs, vector_definition):
        super(SweCoordinate, self).__init__(element, swe_ns)
        self.srs = srs
        self.vector_definition = vector_definition

class SweDataChoice(object):
    def __init__(self, element, swe_ns):
        self._root = element
        self._data_choices = {}

        for item in self._root.findall(nsp("item", swe_ns)):
            name = testXMLAttribute(item, "name")
            self._data_choices[name] = []
            for child in item.find(nsp("DataRecord", swe_ns)):
                # Create an array of possible columns
                x = get_field_object(child, swe_ns)
                if x is not None:
                    self._data_choices[name].append(x)
    def get_fields(self, choice=None):
        if choice is None:
            raise ValueError("Must pass a value to retrieve columns for a DataChoice element")
        try:
            return self._data_choices[choice]
        except KeyError:
            raise KeyError("DataChoice '%s' not found" % choice)

class SweVector(object):
    def __init__(self, element, swe_ns):
        self._root = element
        self._fields = []
        self.definition = testXMLAttribute(self._root, "definition")
        self.srs = testXMLAttribute(self._root, "referenceFrame")
        for coord in self._root.findall(nsp("coordinate", swe_ns)):
            self._fields.append(SweCoordinate(coord, swe_ns, self.srs, self.definition))
    def get_fields(self, choice=None):
        return self._fields

class SweTime(object):
    def __init__(self, element, swe_ns):
        self._root = element
        t = SweField(self._root, swe_ns)
        t.name = "time"
        t.axis = "time"
        self._fields = [t]
    def get_fields(self, choice=None):
        return self._fields

class SweValues(object):
    """
        We are only supporting block_seperators that are newlines.
        This is a Python limitation.  The csv modules does not 
        support custom line (block) seperators.
    """
    def __init__(self, element, encoding):
        text = StringIO.StringIO(testXMLValue(element))
        reader = csv.reader(text, delimiter=encoding.token_separator)
        self.csv = ((r.strip() for r in row) for row in reader)

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