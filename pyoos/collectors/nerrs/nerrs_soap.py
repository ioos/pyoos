from __future__ import (absolute_import, division, print_function)

from pyoos.parsers.nerrs import NerrsToPaegan
from pyoos.collectors.collector import Collector
from pyoos.utils.etree import etree
from owslib.util import testXMLValue

from shapely.geometry import Point, box
import requests


class NerrsSoap(Collector):
    def __init__(self, **kwargs):
        """
        :param wildcard: string for optional token-based access mechanism.
        """
        super(NerrsSoap, self).__init__()
        self.wsdl_url = 'http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl'
        self.wildcard = kwargs.get("wildcard")
        self.stations = self.get_stations()

    def get_station(self, feature):
        for s in self.stations:
            if s['Station_Code'].lower() == feature.lower():
                return s

    def get_stations(self):
        if self.wildcard is not None:
            xml_str = """
            <exportStationCodesXMLNew xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <wildcard xsi:type="xsd:string">OPTIONALVALUE</wildcard>
            </exportStationCodesXMLNew>
            """
            xml_obj = etree.fromstring(xml_str)
            xml_obj.find(".//wildcard").text = self.wildcard
        else:
            """<exportStationCodesXMLNew />"""
            xml_obj = etree.Element("exportStationCodesXMLNew")

        env = self._makesoap(xml_obj)

        stats = []
        for data in env.findall(".//data"):
            s = {}
            for child in data:
                val = testXMLValue(child)
                if val is None:
                    val = ""
                s[child.tag] = val
            lon = float(s['Longitude'])
            s['Longitude'] = lon if lon < 0 else -lon
            s['Latitude'] = float(s['Latitude'])
            stats.append(s)

        return stats

    def _makesoap(self, xmlelement):
        request = """<?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                            xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                            xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
            <SOAP-ENV:Body>
                REQUEST
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """
        enve = etree.fromstring(request)

        body = enve.find(".//{%s}Body" % "http://schemas.xmlsoap.org/soap/envelope/")
        body.append(xmlelement)

        headers = {
            "SOAPAction"        : "\"\"",
        }
        r = requests.post(self.wsdl_url, data=etree.tostring(enve), headers=headers)
        return etree.fromstring(r.text[38:]).find(".//returnData")

    def list_features(self):
        return sorted([s['Station_Code'] for s in self.stations], key=str.lower)

    def list_variables(self, feature=None):
        ignore_vars = ["", None]
        if feature is None:
            stationvars = [s['Params_Reported'].split(",") for s in self.stations]
            # Combine the sublists, ignoring bad names.
            allvars = [v for sublist in stationvars for v in sublist if v not in ignore_vars]
            # Unique the var list.
            return sorted(list(set(allvars)), key=str.lower)
        else:
            s = self.get_station(feature)
            return sorted([v for v in list(set(s['Params_Reported'].split(","))) if v not in ignore_vars], key=str.lower)

    def collect(self):
        results = self.raw()
        return NerrsToPaegan(results, nerrs_stations=self.stations).feature

    def raw(self, **kwargs):
        # These are the features we will actually query against
        query_features = []

        if self.bbox is None and self.features is None:
            raise ValueError("NERRS requires a BBOX or Feature filter")

        if self.bbox is not None and self.features is not None:
            print("Both a BBox and Feature filter is defined, BBOX takes precedence.")

        # BBox takes precedence over features
        if self.bbox is not None:
            test_box = box(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
            # Set the features and call collect again
            for s in self.stations:
                p = Point(float(s["Longitude"]), float(s["Latitude"]))
                if test_box.intersects(p):
                    query_features.append(s['Station_Code'])
        else:
            query_features = self.features

        if query_features is not None and len(query_features) > 0:

            results = {}
            for f in query_features:
                if self.start_time is not None and self.end_time is not None:
                    # Date range query
                    soap_env = self._build_exportAllParamsDateRangeXMLNew(f)
                else:
                    # Not a date range query
                    soap_env = self._build_exportSingleParamXMLNew(f)

                if soap_env is not None:
                    response = self._makesoap(soap_env)
                    results[f] = etree.tostring(response)

            return results

        return None

    def _build_exportAllParamsDateRangeXMLNew(self, feature):
        xml_str = """
        <exportAllParamsDateRangeXMLNew xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <station_code xsi:type="xsd:string">owcowmet</station_code>
            <mindate xsi:type="xsd:string">05/29/2013</mindate>
            <maxdate xsi:type="xsd:string">05/31/2013</maxdate>
            <param xsi:type="xsd:string">WSpd,WDir</param>
            <wildcard xsi:type="xsd:string">OPTIONALVALUE</wildcard>
        </exportAllParamsDateRangeXMLNew>
        """
        xml_obj = etree.fromstring(xml_str)

        if self.wildcard is not None:
            xml_obj.find(".//wildcard").text = self.wildcard

        xml_obj.find(".//mindate").text = self.start_time.strftime('%m/%d/%Y')
        xml_obj.find(".//maxdate").text = self.end_time.strftime('%m/%d/%Y')

        feature_vars = self.list_variables(feature=feature)
        if len(feature_vars) == 0:
            # This feature has no variables, skip it
            return None
        else:
            if self.variables is not None:
                # Query for vars this station has
                queryvars = set(self.variables).intersection(feature_vars)
                if len(queryvars) == 0:
                    # Skip this feature.. it doesn't have any of the requested variables
                    return None
                xml_obj.find(".//param").text = ",".join(queryvars)
            else:
                # No variable subset requested
                xml_obj.find(".//param").text = ",".join(feature_vars)

        # Set station and recs
        xml_obj.find(".//station_code").text = feature
        return xml_obj

    def _build_exportSingleParamXMLNew(self, feature):
        xml_str = """
        <exportSingleParamXMLNew xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <station_code xsi:type="xsd:string">FILLME</station_code>
            <recs xsi:type="xsd:string">FILLME</recs>
            <param xsi:type="xsd:string">FILLME</param>
            <wildcard xsi:type="xsd:string">OPTIONALVALUE</wildcard>
        </exportSingleParamXMLNew>
        """
        xml_obj = etree.fromstring(xml_str)

        if self.wildcard is not None:
            xml_obj.find(".//wildcard").text = self.wildcard

        # Set parameters
        feature_vars = self.list_variables(feature=feature)
        if len(feature_vars) == 0:
            # This feature has no variables, skip it
            return None
        else:
            if self.variables is not None:
                # Query for vars this station has
                queryvars = set(self.variables).intersection(feature_vars)
                if len(queryvars) == 0:
                    # Skip this feature.. it doesn't have any of the requested variables
                    return None
                xml_obj.find(".//param").text = ",".join(queryvars)
            else:
                # No variable subset requested
                xml_obj.find(".//param").text = ",".join(feature_vars)

        # Set station and recs
        xml_obj.find(".//station_code").text = feature
        xml_obj.find(".//recs").text = "100"
        return xml_obj
