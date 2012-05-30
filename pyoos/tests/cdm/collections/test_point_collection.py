import unittest
from pyoos.cdm.features.point import Point
from shapely.geometry import Point as sPoint
from pyoos.cdm.utils.member import Member
from pyoos.cdm.collections.point_collection import PointCollection
import datetime

class PointCollectionTest(unittest.TestCase):
    def test_point_collection(self):
        dt1 = datetime.date(2007, 12, 5)
        p1 = Point()
        p1.time = dt1
        p1.location = sPoint(-180, -90, 0)
        member1 = Member(value=5.4, unit='m', name='Sea Surface Height', description='sea height', standard='sea_surface_height')
        member2 = Member(value=8.1, unit='m', name='Wave Height', description='wave height', standard='wave_height')
        p1.add_member(member1)
        p1.add_member(member2)

        dt2 = datetime.date(2008, 2, 14)
        p2 = Point()
        p2.time = dt2
        p2.location = sPoint(-120, 50, 10)
        member3 = Member(value=5.4, unit='m', name='Sea Surface Height', description='sea height', standard='sea_surface_height')
        member4 = Member(value=8.1, unit='m', name='Wave Height', description='wave height', standard='wave_height')
        p2.add_member(member3)
        p2.add_member(member4)

        pc = PointCollection(elements=[p1,p2])
        pc.calculate_bounds()

        assert pc.size == 2
        assert pc.time_range[0] == dt1
        assert pc.time_range[-1] == dt2
        assert pc.depth_range[0] == p1.location.z
        assert pc.depth_range[-1] == p2.location.z
        assert pc.upper_right().equals(sPoint(p2.location.x, p2.location.y))
        assert pc.lower_left().equals(sPoint(p1.location.x, p1.location.y))
        