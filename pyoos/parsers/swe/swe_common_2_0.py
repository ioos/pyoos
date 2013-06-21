from owslib.util import nspath as nsp
from owslib.util import nspath_eval as nspv
from owslib.namespaces import Namespaces
from owslib.util import testXMLAttribute, testXMLValue, InfiniteDateTime, NegativeInfiniteDateTime
from owslib.crs import Crs
import csv
import StringIO
import copy

from dateutils import parser
from datetime import timedelta

def get_namespaces():
    ns = Namespaces()
    return ns.get_namespaces(["swe20", "xlink"])
namespaces = get_namespaces()

def make_pair(string, cast=None):
    if string is None
        return None

    string = string.split(" ")
    if cast is not None:
        try:
            string = map(lambda x: cast(x), string)
        except:
            string = None

    return tuple(string)

def nspv(path):
    return nspath_eval(path, namespaces)

def get_uom(element):
    uom = testXMLAttribute(element.find(nspv("swe20:uom")), "code")
    if uom is None:
        uom = testXMLAttribute(element.find(nspv("swe20:uom")), nspv("xlink:href"))
    return uom

AnyScalar    = map(lamda x: nspv(x), ["swe20:Boolean", "swe20:Count", "swe20:Quantity", "swe20:Time", "swe20:Category", "swe:Text"])
AnyNumerical = map(lamda x: nspv(x), ["swe20:Count", "swe20:Quantity", "swe20:Time"])
AnyRange     = map(lamda x: nspv(x), ["swe20:QuantityRange", "swe20:TimeRange", "swe20:CountRange", "swe20:CategoryRange"])

class SweCommon_2_0(object):
    def __init__(self, **kwargs):
        pass

class NamedObject(object):
    def __init__(self, element):
        # No call to super(), the type object will process that.
        self.name           = testXMLAttribute(element, "name")
        self.type           = call(element[0].tag.split("}")[1])(element[0])
    # Revert to the type if attribute does not exists
    def __getattr__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return getattr(self.type, name)

class AbstractSWE(object):
    def __init__(self, element):
        # Attributes
        self.id             = testXMLAttribute(element,"id")   # string, optional

        # Elements
        self.extention      = []                                    # anyType, min=0, max=X

class AbstractSWEIdentifiable(AbstractSWE):
    def __init__(self, element):
        # Elements
        self.identifier     = testXMLValue(element.find(nspv("swe20:identifier")))    # anyURI, min=0
        self.label          = testXMLValue(element.find(nspv("swe20:label")))         # string, min=0
        self.description    = testXMLValue(element.find(nspv("swe20:description")))   # string, min=0

class AbstractDataComponent(AbstractSWEIdentifiable):
    def __init__(self, element):
        # Attributes
        self.definition     = testXMLAttribute(element,"definition")        # anyURI, required
        self.updatable      = testXMLAttribute(element,"updatable")         # boolean, optional
        self.optional       = testXMLAttribute(element,"optional") or False # boolean, default=False

class AbstractSimpleComponent(AbstractDataComponent):
    def __init__(self, element):
        # Attributes
        self.referenceFrame = testXMLAttribute(element,"referenceFrame")    # anyURI, optional
        self.axisID         = testXMLAttribute(element."axisID")            # string, optional

        # Elements
        self.quality        = filter(None, [Quality(e) for e in element.findall(nspv("swe20:quality"))])
        self.nilValues      = NilValues(element.find(nspv("swe20:nilValues")))

class Quality(object):
    def __new__(cls, element):
        t = element.tag.split("}")[1]
        if t == "Quantity":
            return Quantity.__new__(element)
        elif t == "QuantityRange":
            return QuantityRange.__new__(element)
        elif t == "Category":
            return Category.__new__(element)
        elif t == "Text":
            return Text.__new__(element)
        else
            return None

class NilValues(AbstractSWE):
    def __init__(self, element):
        self.nilValue           = filter(None, [nilValue(x) for x in element.findall(nspv("swe20:nilValue"))]) # string, min=0, max=X

class nilValue(object):
    def __init__(self, element):
        self.reason             = testXMLAttribute(element, "reason")
        self.value              = testXMLValue(element)

class AllowedTokens(AbstractSWE):
    def __init__(self, element):
        self.value              = filter(None, [testXMLValue(x) for x in element.findall(nspv("swe20:value"))]) # string, min=0, max=X
        self.pattern            = testXMLValue(element.find(nspv("swe20:pattern")))                             # string (Unicode Technical Standard #18, Version 13), min=0

class AllowedValues(AbstractSWE):
    def __init__(self, element):
        self.value              = map(lambda x: float(x), filter(None, [testXMLValue(x) for x in element.findall(nspv("swe20:value"))]))
        self.interval           = filter(None, [make_pair(testXMLValue(x)) for x in element.findall(nspv("swe20:interval"))])
        self.significantFigures = testXMLValue(element.find(nspv("swe20:significantFigures")))                                   # integer, min=0

class AllowedTimes(AbstractSWE):
    def __init__(self, element):
        self.value              = filter(None, [testXMLValue(x) for x in element.findall(nspv("swe20:value"))])
        self.interval           = filter(None, [make_pair(testXMLValue(x)) for x in element.findall(nspv("swe20:interval"))])
        self.significantFigures = testXMLValue(element.find(nspv("swe20:significantFigures")))               # integer, min=0

class Boolean(AbstractSimpleComponent):
    def __init__(self, element):
        # Elements
        """
        6.2.1 Boolean
            A Boolean representation of a property can take only two values that should be “true/false” or “yes/no”.
        """
        value          = testXMLValue(element.find(nspv("swe20:value")))   # boolean, min=0, max=1
        if value.lower() in ["yes","true"]:
            self.value = True
        elif value.lower() in ["no","false"]:
            self.value = False
        else:
            self.value = None


class Text(AbstractSimpleComponent):
    def __init__(self, element):
        # Elements
        """
        Req 6. A textual representation shall at least consist of a character string.
        """
        self.constraint     = AllowedTokens(element.find(nspv("swe:constraint/swe20:AllowedTokens")))   # AllowedTokens, min=0, max=1
        self.value          = testXMLValue(element.find(nspv("swe20:value")))                           # string, min=0, max=1


class Category(AbstractSimpleComponent):
    def __init__(self, element):
        # Elements
        self.codeSpace      = testXMLAttribute(element.find(nspv("swe20:codeSpace")), nspv("xlink:href"))   # Reference, min=0, max=1
        self.constraint     = AllowedTokens(element.find(nspv("swe:constraint/swe20:AllowedTokens")))       # AllowedTokens, min=0, max=1
        self.value          = testXMLValue(element.find(nspv("swe20:value")))                               # string, min=0, max=1

class CategoryRange(Category):
    def __init__(self, element):
        # Elements
        value               = testXMLValue(element.find(nspv("swe20:value")))
        self.values         = make_pair(value) if value is not None else None

class Count(AbstractSimpleComponent):
    def __init__(self, element):
        # Elements
        self.constraint     = AllowedValues(element.find(nspv("swe:constraint/swe20:AllowedValues")))   # AllowedValues, min=0, max=1
        self.value          = testXMLValue(element.find(nspv("swe20:value")))                           # integer, min=0, max=1

class CountRange(Count):
    def __init__(self, element):
        # Elements
        value               = testXMLValue(element.find(nspv("swe20:value")))
        self.value          = make_pair(value,int) if value is not None else None

class Quantity(AbstractSimpleComponent):
    def __init__(self, element):
        # Elements
        self.uom            = get_uom(element.find(nspv("swe20:uom")))
        self.constraint     = AllowedValues(element.find(nspv("swe:constraint/swe20:AllowedValues")))   # AllowedValues, min=0, max=1
        self.value          = testXMLValue(element.find(nspv("swe20:value")))                           # double, min=0, max=1

class QuantityRange(Quantity):
    def __init__(self, element):
        # Elements
        value               = testXMLValue(element.find(nspv("swe20:value")))
        self.value          = make_pair(value,float) if value is not None else None


def get_time(value, referenceTime, uom):
    try:
        value = parser.parse(value)

    except ValueError: # Most likely an integer/float using a referenceTime
        try:
            if uom.lower() == "s":
                value  = referenceTime + timedelta(seconds=float(value))
            elif uom.lower() == "min":
                value  = referenceTime + timedelta(minutes=float(value))
            elif uom.lower() == "h":
                value  = referenceTime + timedelta(hours=float(value))
            elif uom.lower() == "d":
                value  = referenceTime + timedelta(days=float(value))
        
        except ValueError:
            pass

    except OverflowError: # Too many numbers (> 10) or INF/-INF
        if value.lower() == "inf":
            value  = InfiniteDateTime()
        elif value.lower() = "-inf":
            value  = NegativeInfiniteDateTime()

    return value


class Time(AbstractSimpleComponent):
    def __init__(self, element):
        # Elements
        self.constraint         = AllowedTimes(element.find(nspv("swe:constraint/swe20:AllowedTimes")))     # AllowedTimes, min=0, max=1
        self.uom                = get_uom(element.find(nspv("swe20:uom")))

        # Attributes
        self.localFrame         = testXMLAttribute(element,"localFrame")                                    # anyURI, optional
        try:
            self.referenceTime  = parser.parse(testXMLAttribute(element,"referenceTime"))                   # dateTime, optional
        except ValueError:
            self.referenceTime  = None

        value                   = testXMLValue(element.find(nspv("swe20:value")))                           # TimePosition, min=0, max=1
        self.value              = get_time(value, self.referenceTime, self.uom)


class TimeRange(AbstractSimpleComponent):
    def __init__(self, element):
        # Elements
        self.constraint         = AllowedTimes(element.find(nspv("swe:constraint/swe20:AllowedTimes"))) # AllowedTimes, min=0, max=1
        self.uom                = get_uom(element.find(nspv("swe20:uom")))

        # Attributes
        self.localFrame         = testXMLAttribute(element,"localFrame")                                # anyURI, optional
        try:
            self.referenceTime  = parser.parse(testXMLAttribute(element,"referenceTime"))               # dateTime, optional
        except ValueError:
            self.referenceTime  = None

        values                  = make_pair(testXMLValue(element.find(nspv("swe20:value"))))            # TimePosition, min=0, max=1
        self.value              = [get_time(t, self.referenceTime, self.uom) for t in values]

class DataRecord(AbstractDataComponent):
    def __init__(self, element):
        # Elements
        self.field          = [Field(x) for x in element.findall(nspv("swe20:field"))]
    def get_by_name(self, name):
        return next(x for x in self.item if x.name == name, None) 

class Field(NamedObject):
    def __init__(self, element):
        super(Field, self).__init__(element)


class Vector(AbstractDataComponent):
    def __init__(self, element):
        # Elements
        self.coordinate     = [Coordinate(x) for x in element.findall(nspv("swe20:field"))]

        # Attributes
        self.referenceFrame = testXMLAttribute(element,"referenceFrame")        # anyURI, required
        self.localFrame     = testXMLAttribute(element,"localFrame")            # anyURI, optional       
    def get_by_name(self, name):
        return next(x for x in self.item if x.name == name, None)

class Coordinate(NamedObject):
    def __init__(self, element):
        super(Coordinate, self).__init__(element)
        if self.type.tag not in AnyNumerical:
            print "Coordinate does not appear to be an AnyNumerical member"


class DataChoice(AbstractDataComponent):
    def __init__(self, element):
        self.item           = [Item(x) for x in element.findall(nspv("swe20:item"))]
    def get_by_name(self, name):
        return next(x for x in self.item if x.name == name, None)

class Item(NamedObject):
    def __init__(self, element):
        super(Item, self).__init__(element)


class DataArray(AbstractDataComponent):
    def __init__(self, element):
        self.elementCount   = element.find(nspv("swe20:elementCount/swe20:Count"))      # required
        self.elementType    = ElementType(element.find(nspv("swe20:elementType")))      # required
        self.encoding       = AbstractEncoding(element.find(nspv("swe20:encoding")))
        self.values         = testXMLValue(element.find(nspv("swe:values")))

class Matrix(AbstractDataComponent):
        self.elementCount   = element.find(nspv("swe20:elementCount/swe20:Count"))      # required
        self.elementType    = ElementType(element.find(nspv("swe20:elementType")))      # required
        self.encoding       = AbstractEncoding(element.find(nspv("swe20:encoding")))
        self.values         = testXMLValue(element.find(nspv("swe:values")))
        self.referenceFrame = testXMLAttribute(element, "referenceFrame")               # anyURI, required
        self.localFrame     = testXMLAttribute(element, "localFrame")                   # anyURI, optional

class DataStream(AbstractSWEIdentifiable):
    def __init__(self, element):
        self.elementCount   = element.find(nspv("swe20:elementCount/swe20:Count"))      # optional
        self.elementType    = ElementType(element.find(nspv("swe20:elementType")))      # optional
        self.encoding       = AbstractEncoding(element.find(nspv("swe20:encoding")))
        self.values         = testXMLValue(element.find(nspv("swe:values")))

class ElementType(NamedObject):
    def __init__(self, element):
        super(Item, self).__init__(element)

class AbstractEncoding(object):
    def __new__(cls, element):
        t = element.tag.split("}")[1]
        if t == "TextEncoding":
            return super(AbstractEncoding, cls).__new__(TextEncoding, element)
        elif t == "XMLEncoding"
            return super(AbstractEncoding, cls).__new__(XMLEncoding, element)            
        elif t == "BinaryEncoding":
            return super(AbstractEncoding, cls).__new__(BinaryEncoding, element)
    def __init__(self, element):
        pass

class TextEncoding(AbstractEncoding):
    def __init__(self, element):
        self.tokenSeperator         = testXMLAttribute(element, "tokenSeperator")               # string,  required
        self.blockSeperator         = testXMLAttribute(element, "blockSeperator")               # string,  required
        self.decimalSeperator       = testXMLAttribute(element, "decimalSeperator") or "."      # string,  optional, default="."
        self.collapseWhiteSpaces    = testXMLAttribute(element, "collapseWhiteSpaces") or True  # boolean, optional, default=True

class XMLEncoding(AbstractEncoding):
    def __init__(self, element):
        pass

class BinaryEncoding(AbstractEncoding):
    def __init__(self, element):
        raise NotImplementedError