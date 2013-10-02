from pyoos.utils.etree import etree
from owslib.namespaces import Namespaces
from owslib.util import testXMLValue
from owslib.util import nspath_eval as nspv
from owslib.crs import Crs
from shapely.geometry import box

ns = Namespaces()

class IoosDescribeSensor(object):
    def __new__(cls, element):
        if isinstance(element, str):
            root = etree.fromstring(element)
        else:
            root = element

        if hasattr(root, 'getroot'):
            root = root.getroot()

        XLINK_NS = ns.get_namespace("xlink")
        SWE_NS = [ns.get_versioned_namespace('swe','1.0.1')]
        version = None
        for g in SWE_NS:
            try:
                version = testXMLValue(root.find(".//{%s}field[@name='ioosTemplateVersion']/{%s}Text/{%s}value" % (g,g,g)))
                break
            except:
                raise

        if version == "1.0":
            SML_NS = ns.get_versioned_namespace('sml', '1.0.1')
            try:
                assert testXMLValue(root.find(".//{%s}identifier[@name='networkID']/{%s}Term[@definition='http://mmisw.org/ont/ioos/definition/networkID']/{%s}value" % (SML_NS, SML_NS, SML_NS)))
                from pyoos.parsers.ioos.one.describe_sensor import NetworkDS
                return super(IoosDescribeSensor, cls).__new__(NetworkDS)
            except AssertionError:
                try:
                    assert testXMLValue(root.find(".//{%s}identifier[@name='stationID']/{%s}Term[@definition='http://mmisw.org/ont/ioos/definition/stationID']/{%s}value" % (SML_NS, SML_NS, SML_NS)))
                    from pyoos.parsers.ioos.one.describe_sensor import StationDS
                    return super(IoosDescribeSensor, cls).__new__(StationDS)
                except AssertionError:
                    try:
                        assert testXMLValue(root.find(".//{%s}identifier[@name='sensorID']/{%s}Term[@definition='http://mmisw.org/ont/ioos/definition/sensorID']/{%s}value" % (SML_NS, SML_NS, SML_NS)))
                        from pyoos.parsers.ioos.one.describe_sensor import SensorDS
                        return super(IoosDescribeSensor, cls).__new__(SensorDS)
                    except AssertionError:
                        raise ValueError("Could not determine if this was a Network, Station, or Sensor SensorML document")
        else:
            raise ValueError("Unsupported IOOS version.  Supported: [1.0]")
