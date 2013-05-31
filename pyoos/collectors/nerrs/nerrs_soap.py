from pyoos.collectors.collector import Collector
from pyoos.utils.etree import etree
from owslib.util import testXMLValue

from shapely.geometry import Point, box
import requests
from copy import copy

class NerrsSoap(Collector):
    def __init__(self, **kwargs):
        super(NerrsSoap,self).__init__()
        self.wsdl_url = 'http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl'
        self.stations = self.get_stations()
        
    def get_station(self, feature):
        for s in self.stations:
            if s['Station_Code'].lower() == feature.lower():
                return s

    def get_stations(self):
        data = """<?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" 
                            xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                            xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
            <SOAP-ENV:Body>
            <exportStationCodesXMLNew />
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """.replace("\n","")
        
        env = self._makesoap(etree.fromstring(data))
        stats = []
        for data in env.findall(".//data"):
            s = {}
            for child in data:
                val = testXMLValue(child)
                if val is None:
                    val = ""
                s[child.tag] = val
            stats.append(s)

        return stats


    def _makesoap(self, xmlelement):
        data = etree.tostring(xmlelement)
        headers = {
            "SOAPAction"        : "\"\"",
        }
        r = requests.post(self.wsdl_url, data=data, headers=headers)
        return etree.fromstring(r.text[38:]).find(".//returnData")

    def list_features(self):
        return sorted(map(lambda s: s['Station_Code'], self.stations), key=str.lower)
        
    def list_variables(self, feature=None):
        ignore_vars = ["",None]
        if feature is None:
            stationvars = map(lambda s: s['Params_Reported'].split(","), self.stations)
            # Combine the sublists, ignoring bad names
            allvars = [v for sublist in stationvars for v in sublist if v not in ignore_vars]
            # Unique the var list
            return sorted(list(set(allvars)), key=str.lower)
        else:
            s = self.get_station(feature)
            return sorted([v for v in list(set(s['Params_Reported'].split(","))) if v not in ignore_vars], key=str.lower)
        
    def collect(self):
        results = self.raw()
        # TODO: parse results into Paegan CDM
        return results

        
    def raw(self, **kwargs):

        request = """<?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" 
                            xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                            xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
            <SOAP-ENV:Body>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """
        enve = etree.fromstring(request)

        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        xsd = "http://www.w3.org/2001/XMLSchema"
        soap = 'http://schemas.xmlsoap.org/soap/envelope/'

        query_features = []

        if self.bbox is None and self.features is None:
            raise ValueError("NERRS requires a BBOX or Feature subset")

        # BBox takes precedence over features
        if self.bbox is not None:
            test_box = box(self.bbox[0],self.bbox[1],self.bbox[2],self.bbox[3])
            # Set the features and call collect again
            for s in self.stations:
                p = Point(float(s["Longitude"]), float(s["Latitude"]))
                if test_box.intersects(p):
                    query_features.append(s['Station_Code'])
        else:
            query_features = self.features

        if query_features is not None and len(query_features) > 0:

            results = []
            
            if self.start_time is not None and self.end_time is not None:
                # Temporal Elements
                mindate = etree.Element("mindate")
                mindate.set("{%s}type" % xsi, "xsd:string")
                mindate.text = self.start_time.strftime('%m/%d/%Y')

                maxdate = etree.Element("maxdate")
                maxdate.set("{%s}type" % xsi, "xsd:string")
                maxdate.text = self.end_time.strftime('%m/%d/%Y')

                for f in query_features:
                    """
                    <exportAllParamsDateRangeXMLNew>
                        <station_code xsi:type="xsd:string">owcowmet</station_code>
                        <mindate xsi:type="xsd:string">05/29/2013</mindate>
                        <maxdate xsi:type="xsd:string">05/31/2013</maxdate>
                        <param xsi:type="xsd:string">WSpd,WDir</param>
                    </exportAllParamsDateRangeXMLNew>
                    """
                    param = etree.Element("param")
                    param.set("{%s}type" % xsi, "xsd:string")

                    if self.variables is not None:
                        if len(self.list_variables(feature=f)) == 0:
                            # This feature has no variables, just skip it
                            continue

                        # Query for vars this station has
                        queryvars = set(self.variables).intersection(self.list_variables(feature=f))
                        if len(queryvars) == 0:
                            # Skip this feature
                            continue
                        param.text = ",".join(queryvars)
                    else:
                        param.text = "*"


                    this_request = copy(enve)

                    body = this_request.find("{%s}Body" % soap
                        )
                    export = etree.SubElement(body, "exportAllParamsDateRangeXMLNew")

                    station_code = etree.Element("station_code")
                    station_code.set("{%s}type" % xsi, "xsd:string")
                    station_code.text = f

                    export.append(station_code)
                    export.append(mindate)
                    export.append(maxdate)
                    export.append(param)

                    results.append(self._makesoap(this_request))
            else:
                # Non Temporal query
                for f in query_features:
                    """
                    <exportSingleParamXMLNew>
                        <station_code xsi:type="xsd:string">owcowmet</station_code>
                        <recs xsi:type="xsd:string">100</recs>
                        <param xsi:type="xsd:string">WSpd,WDir</param>
                    </exportSingleParamXMLNew>
                    """
                    param = etree.Element("param")
                    param.set("{%s}type" % xsi, "xsd:string")

                    if self.variables is not None:
                        if len(self.list_variables(feature=f)) == 0:
                            # This feature has no variables, just skip it
                            continue

                        # Query for vars this station has
                        queryvars = set(self.variables).intersection(self.list_variables(feature=f))
                        if len(queryvars) == 0:
                            # Skip this feature
                            continue
                        param.text = ",".join(queryvars)
                    else:
                        param.text = ",".join(self.list_variables(feature=f))

                    this_request = copy(enve)

                    body = this_request.find("{%s}Body" % soap
                        )
                    export = etree.SubElement(body, "exportSingleParamXMLNew")

                    station_code = etree.Element("station_code")
                    station_code.set("{%s}type" % xsi, "xsd:string")
                    station_code.text = f

                    recs = etree.Element("recs")
                    recs.set("{%s}type" % xsi, "xsd:string")
                    recs.text = "100"

                    export.append(station_code)
                    export.append(recs)
                    export.append(param)

                    results.append(etree.tostring(self._makesoap(this_request)))

            return results

        return None