# -*- coding: utf-8 -*-
import unittest
from pyoos.cdm.features.point import Point
from shapely.geometry import Point as sPoint
from pyoos.cdm.utils.member import Member
from pyoos.cdm.features.profile import Profile
from datetime import datetime

class ProfileTest(unittest.TestCase):
    def test_profile(self):
        dt1 = datetime(2012, 1, 1, 12, 0)
        p1 = Point()
        p1.time = dt1
        p1.location = sPoint(-120, 50, 0)
        member1 = Member(value=34.7, unit='°C', name='Water Temperatire', description='water temperature', standard='sea_water_temperature')
        member2 = Member(value=80, unit='PSU', name='Salinity', description='salinity', standard='salinity')
        p1.add_member(member1)
        p1.add_member(member2)

        dt2 = datetime(2012, 1, 1, 12, 10)
        p2 = Point()
        p2.time = dt2
        p2.location = sPoint(-120, 50, 10)
        member3 = Member(value=34.1, unit='°C', name='Water Temperatire', description='water temperature', standard='sea_water_temperature')
        member4 = Member(value=70, unit='PSU', name='Salinity', description='salinity', standard='salinity')
        p2.add_member(member3)
        p2.add_member(member4)

        dt3 = datetime(2012, 1, 1, 12, 20)
        p3 = Point()
        p3.time = dt3
        p3.location = sPoint(-120, 50, 20)
        member5 = Member(value=32.6, unit='°C', name='Water Temperatire', description='water temperature', standard='sea_water_temperature')
        member6 = Member(value=60, unit='PSU', name='Salinity', description='salinity', standard='salinity')
        p3.add_member(member5)
        p3.add_member(member6)

        pc = Profile(elements=[p1,p2,p3])
        pc.location = sPoint(-120, 50)
        pc.time = dt1
        pc.calculate_bounds()

        assert pc.size == 3
        assert pc.time == dt1
        assert len(pc.time_range) == 3
        assert pc.time_range[0] == dt1
        assert pc.time_range[-1] == dt3
        assert len(pc.depth_range) == 3
        assert pc.depth_range[0] == p1.location.z
        assert pc.depth_range[-1] == p3.location.z
        assert pc.upper_right().equals(pc.location)
        assert pc.lower_left().equals(pc.location)