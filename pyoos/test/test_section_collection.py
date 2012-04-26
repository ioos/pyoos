# -*- coding: utf-8 -*-
import random
import unittest
from pyoos.cdm.features.point import Point
from shapely.geometry import Point as sPoint
from pyoos.cdm.utils.member import Member
from pyoos.cdm.features.profile import Profile
from datetime import datetime, timedelta
from pyoos.cdm.features.section import Section
from pyoos.cdm.collections.section_collection import SectionCollection

class SectionCollectionTest(unittest.TestCase):
    def test_section_collection(self):

        s_collection = SectionCollection()

        # 20 sections
        for x in xrange(0,20):

            day = 1
            hour = 0
            sc = Section()
            dt = None

            # 10 profiles per section
            for x in xrange(0,10):
                lat = random.randint(40,44)
                lon = random.randint(-74,-70)
                loc = sPoint(lon,lat,0)
                minute = 0
                dt = datetime(2012, 4, day, hour, minute)
                hour += 1

                prof = Profile()
                prof.location = loc
                prof.time = dt

                # Each with 20 depths
                for y in xrange(0,20):
                    p = Point()
                    p.time = dt
                    p.location = sPoint(loc.x, loc.y, y)
                    m1 = Member(value=random.uniform(30,40), unit='°C', name='Water Temperatire', description='water temperature', standard='sea_water_temperature')
                    m2 = Member(value=random.uniform(80,100), unit='PSU', name='Salinity', description='salinity', standard='salinity')
                    p.add_member(m1)
                    p.add_member(m2)
                    prof.add_element(p)
                    # Next depth is 2 minutes from now
                    dt = dt + timedelta(minutes=2)

                sc.add_element(prof)
                
            s_collection.add_element(sc)

        s_collection.calculate_bounds()

        assert s_collection.depth_range[0] == 0
        assert s_collection.depth_range[-1] == 19
        assert s_collection.time_range[0] == datetime(2012, 4, 1, 0)

        for section in s_collection:
            assert section.type == "Section"
            for profile in section:
                assert profile.type == "Profile"
                for point in profile:
                    assert point.type == "Point"

        for point in s_collection.flatten():
            assert point.type == "Point"