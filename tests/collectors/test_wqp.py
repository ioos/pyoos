# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import unittest
from pytest import raises
from pyoos.collectors.wqp.wqp_rest import WqpRest
from pyoos.parsers.wqx.wqx_outbound import WqxOutbound


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
        self.c.filter(features=["21IOWA-10070005"])
        meta, data = self.c.raw()

        org = WqxOutbound(meta).organizations[0]

        # OrganizationDescription
        assert org.description.name == u"Iowa Dept. of  Natural Resources"
        assert org.description.id == u"21IOWA"

        # MonitoringLocation
        assert org.locations[0].id == u"21IOWA-10070005"
        assert org.locations[0].name == u"Cedar River Upstream of Waterloo/Cedar Falls"
        assert org.locations[0].type == u"River/Stream"
        assert org.locations[0].description.startswith(u"Below the dam of Old Highway 218 in Cedar Falls")
        assert org.locations[0].huc == u"07080205"
        assert org.locations[0].latitude == u"42.5392"
        assert org.locations[0].longitude == u"-92.4495"
        assert org.locations[0].vertical_measure_value == u"854"
        assert org.locations[0].vertical_measure_units == u"ft"
        assert org.locations[0].country == u"US"
        assert org.locations[0].state == u"19"
        assert org.locations[0].county == u"013"

    def test_wqp_results_metadata(self):
        self.c.filter(features=["21IOWA-10070005"])
        meta, data = self.c.raw()

        # OrganizationDescription
        org = WqxOutbound(data).organizations[0]
        assert org.description.name == u"Iowa Dept. of  Natural Resources"
        assert org.description.id == u"21IOWA"

    def test_bad_wqp_site(self):
        self.c.filter(features=["s"])
        rmeta, data = self.c.raw()

        with raises(AttributeError):
            print(data.organization)

    def test_into_dsg(self):
        # First feature filter
        self.c.filter(features=["21IOWA-10070005"])
        station_collection = self.c.collect()
        station_collection.calculate_bounds()

        assert station_collection.size == 1
        station = station_collection.elements[0]
        assert len(station.get_unique_members()) == 240
        assert station.location.x == -92.4495
        assert station.location.y == 42.5392
        assert station.location.z == float(854 / 3.28084)

        # Second variable filter
        self.c.filter(variables=["Mercury"])
        station_collection = self.c.collect()
        station_collection.calculate_bounds()

        assert station_collection.size == 1
        station = station_collection.elements[0]
        assert len(station.get_unique_members()) == 1
