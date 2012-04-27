# -*- coding: utf-8 -*-
import unittest
import random
from pyoos.cdm.features.point import Point
from pyoos.cdm.features.trajectory import Trajectory
from shapely.geometry import Point as sPoint
from pyoos.cdm.utils.member import Member
from datetime import datetime

class TrajectoryTest(unittest.TestCase):
    def test_trajectory(self):
        dt1 = datetime(2012, 4, 1, 0)
        p1 = Point()
        p1.time = dt1
        p1.location = sPoint(-121, 49, 40)
        member1 = Member(value=random.uniform(30,40), unit='°C', name='Water Temperatire', description='water temperature', standard='sea_water_temperature')
        member2 = Member(value=random.uniform(80,100), unit='PSU', name='Salinity', description='salinity', standard='salinity')
        p1.add_member(member1)
        p1.add_member(member2)

        dt2 = datetime(2012, 4, 1, 1)
        p2 = Point()
        p2.time = dt2
        p2.location = sPoint(-120, 50, 60)
        member3 = Member(value=random.uniform(30,40), unit='°C', name='Water Temperatire', description='water temperature', standard='sea_water_temperature')
        member4 = Member(value=random.uniform(80,100), unit='PSU', name='Salinity', description='salinity', standard='salinity')
        p2.add_member(member3)
        p2.add_member(member4)

        tr = Trajectory(elements=[p1,p2])
        tr.calculate_bounds()

        assert len(tr.get_path()) == 2
        assert tr.size == 2
        assert tr.type == "Trajectory"
        assert tr.time_range[0] == dt1
        assert tr.time_range[-1] == dt2
        assert tr.depth_range[0] == p1.location.z
        assert tr.depth_range[-1] == p2.location.z
        assert tr.upper_right().equals(sPoint(p2.location.x, p2.location.y))
        assert tr.lower_left().equals(sPoint(p1.location.x, p1.location.y))
        