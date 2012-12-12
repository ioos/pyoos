# -*- coding: utf-8 -*-

import unittest
from pytest import raises
from pyoos.collectors.wqp.wqp_rest import WqpRest
from datetime import datetime, timedelta
from pyoos.utils.asatime import AsaTime

class WqpTest(unittest.TestCase):

    def setUp(self):
        self.c = WqpRest()

    def test_wqp_sites_metadata(self):
        """
        <WQX xmlns="http://qwwebservices.usgs.gov/schemas/WQX-Outbound/2_0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://qwwebservices.usgs.gov/schemas/WQX-Outbound/2_0/ http://qwwebservices.usgs.gov/schemas/WQX-Outbound/2_0/index.xsd">
            <Organization>
                <OrganizationDescription>
                    <OrganizationIdentifier>21IOWA</OrganizationIdentifier>
                    <OrganizationFormalName>Iowa Dept. of  Natural Resources</OrganizationFormalName>
                </OrganizationDescription>
                <MonitoringLocation>
                    <MonitoringLocationIdentity>
                        <MonitoringLocationIdentifier>21IOWA-10070005</MonitoringLocationIdentifier>
                        <MonitoringLocationName>Cedar River Upstream of Waterloo/Cedar Falls</MonitoringLocationName>
                        <MonitoringLocationTypeName>River/Stream</MonitoringLocationTypeName>
                        <MonitoringLocationDescriptionText>Below the dam of Old Highway 218 in Cedar Falls.¿Upstream City Site.</MonitoringLocationDescriptionText>
                        <HUCEightDigitCode>07080205</HUCEightDigitCode>
                    </MonitoringLocationIdentity>
                    <MonitoringLocationGeospatial>
                        <LatitudeMeasure>42.5392</LatitudeMeasure>
                        <LongitudeMeasure>-92.4495</LongitudeMeasure>
                        <SourceMapScaleNumeric>000</SourceMapScaleNumeric>
                        <HorizontalCollectionMethodName>Interpolation-Map</HorizontalCollectionMethodName>
                        <HorizontalCoordinateReferenceSystemDatumName>NAD27</HorizontalCoordinateReferenceSystemDatumName>
                        <VerticalMeasure>
                            <MeasureValue>854</MeasureValue>
                            <MeasureUnitCode>ft</MeasureUnitCode>
                        </VerticalMeasure>
                        <VerticalCollectionMethodName>Topographic Map Interpolation</VerticalCollectionMethodName>
                        <VerticalCoordinateReferenceSystemDatumName>NGVD29</VerticalCoordinateReferenceSystemDatumName>
                        <CountryCode>US</CountryCode>
                        <StateCode>19</StateCode>
                        <CountyCode>013</CountyCode>
                    </MonitoringLocationGeospatial>
                </MonitoringLocation>
            </Organization>
        </WQX>
        """
        #self.c.start_time = AsaTime.parse("2009-08-01")
        #self.c.end_time = AsaTime.parse("2009-09-10")
        
        results = self.c.get_metadata(siteid="21IOWA-10070005")

        # OrganizationDescription
        assert results.organization.name == u"Iowa Dept. of  Natural Resources"
        assert results.organization.id == u"21IOWA"

        # MonitoringLocation
        assert results.location.id == u"21IOWA-10070005"
        assert results.location.name == u"Cedar River Upstream of Waterloo/Cedar Falls"
        assert results.location.type == u"River/Stream"
        assert results.location.description == u"Below the dam of Old Highway 218 in Cedar Falls.¿Upstream City Site."
        assert results.location.huc == u"07080205"
        assert results.location.latitude == u"42.5392"
        assert results.location.longitude == u"-92.4495"
        assert results.location.vertical_measure_value == u"854"
        assert results.location.vertical_measure_units == u"ft"
        assert results.location.country == u"US"
        assert results.location.state == u"19"
        assert results.location.county == u"013"
        

    def test_wqp_results_metadata(self):
        #self.c.start_time = datetime.today() - timedelta(weeks=520)
        #self.c.start_time = AsaTime.parse("2009-08-01")
        #self.c.end_time = AsaTime.parse("2009-09-10")
        
        results = self.c.get_data(siteid="21IOWA-10070005")
        
        # OrganizationDescription
        assert results.organization.name == u"Iowa Dept. of  Natural Resources"
        assert results.organization.id == u"21IOWA"
        

    def test_bad_wqp_site(self):
        results = self.c.get_metadata(siteid="s")
        with raises(AttributeError):
            print results.organization