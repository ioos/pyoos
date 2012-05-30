# -*- coding: utf-8 -*-
import random
import unittest
from pyoos.cdm.features.point import Point
from shapely.geometry import Point as sPoint
from pyoos.cdm.utils.member import Member
from datetime import datetime, timedelta
from pyoos.cdm.features.trajectory import Trajectory
from pyoos.cdm.collections.trajectory_collection import TrajectoryCollection
from pyoos.utils.asalist import AsaList

class TrajectoryCollectionTest(unittest.TestCase):
    def test_trajectory_collection(self):

        t_collection = TrajectoryCollection()

        # 20 trajectories
        for x in xrange(0,20):

            tr = Trajectory()

            month = random.randint(1,12)
            dt = datetime(2012, month, 1, 0)

            # Starting point
            lat = random.randint(40,44)
            lon = random.randint(-74,-70)
            depth = 0

            # 100 points in each trajectory
            for l in xrange(0,100):

                lat += random.uniform(-0.25,0.25)
                lon += random.uniform(-0.25,0.25)
                depth += random.randint(-4,4)
                if depth < 0:
                    depth = 0

                p1 = Point()
                p1.location = sPoint(lon,lat,depth)
                dt += timedelta(hours=1)
                p1.time = dt
                member1 = Member(value=random.uniform(30,40), unit='°C', name='Water Temperature', description='water temperature', standard='sea_water_temperature')
                member2 = Member(value=random.uniform(80,100), unit='PSU', name='Salinity', description='salinity', standard='salinity')
                p1.add_member(member1)
                p1.add_member(member2)

                tr.add_element(p1)
        
            t_collection.add_element(tr)

        t_collection.calculate_bounds()

        assert len(t_collection.time_range) == 2000
        assert len(t_collection.depth_range) == 2000

        for trajectory in t_collection:
            assert trajectory.type == "Trajectory"
            for point in trajectory:
                assert point.type == "Point"

        for point in t_collection.flatten():
            assert point.type == "Point"