import unittest
import os
from datetime import datetime
from shapely.geometry import Point as sPoint
from pyoos.cdm.features.point import Point
from pyoos.cdm.utils.member import Member

class PointTest(unittest.TestCase):
    def test_point(self):
        dt = datetime.utcnow()
        p = Point()
        p.location = sPoint(-123.17, 48.33, 10)
        p.time = dt

        assert p.location.x == -123.17
        assert p.location.y == 48.33
        assert p.location.z == 10
        assert p.time == dt
        assert p.type == "Point"

    def test_set_get_member(self):
        p = Point()
        member = Member(value=5.4, unit='m', name='Sea Surface Height', description='a description', standard='sea_surface_height')
        p.add_member(member)

        assert member == p.get_member(name='Sea Surface Height')