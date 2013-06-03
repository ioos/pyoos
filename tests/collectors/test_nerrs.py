import unittest
from datetime import datetime, timedelta
from pytest import raises
from pyoos.collectors.nerrs.nerrs_soap import NerrsSoap
from shapely.geometry import Point

class NerrTest(unittest.TestCase):

    def setUp(self):
        self.c = NerrsSoap()

    def test_list_nerrs_features(self):
        # The number of features may change... just make sure we get enough
        assert len(self.c.list_features()) > 10

    def test_list_nerrs_variables(self):
        # The number of variables may change... just make sure we get enough
        assert len(self.c.list_variables()) > 10

        station_vars = self.c.list_variables(feature='rkbfbwq')
        assert station_vars == ['Depth', 'DO_mgl', 'DO_pct', 'pH', 'Sal', 'SpCond', 'Temp', 'Turb']

    def test_get_nerrs_raw(self):
        """
            test the station cdm returned from nerrs
        """

        self.c.filter(bbox=(85.0196, 29.6079, 85.089, 29.7791))
        collection = self.c.raw()
        # Five features in the bounding box
        assert len(collection) == 5

        self.c.clear()
        self.c.filter(features=['owcowmet'])
        collection = self.c.raw()
        assert len(collection) == 1

        self.c.filter(features=['owcowmet','rkbfbwq'])
        collection = self.c.raw()
        # both are returned
        assert len(collection) == 2

        ending = datetime.utcnow() - timedelta(days=90)
        starting = ending - timedelta(hours=24)
        self.c.filter(start_time=starting, end_time=ending)
        collection = self.c.raw()
        # both are returned
        assert len(collection) == 2

        self.c.filter(variables=["ATemp"])
        collection = self.c.raw()
        # 'rkbfbwq' does not have ATemp, so it not returned
        assert len(collection) == 1

        self.c.filter(variables=["ATemp","Temp"])
        collection = self.c.raw()
        # both are returned
        assert len(collection) == 2

        # Must specify BBOX or Features subset for NERRS
        self.c.clear()
        self.c.filter(variables=["ATemp","Temp"])
        with raises(ValueError):
            self.c.raw()

        # Test NERRS chaining
        self.c.clear()
        self.c.filter(features=['owcowmet','rkbfbwq']).filter(variables=["ATemp"])
        collection = self.c.raw()
        # only 'owcowmet' returning
        assert len(collection) == 1

        # Test multiple filter types on one call to 'filter'
        self.c.clear()
        self.c.filter(features=['owcowmet','rkbfbwq'], variables=["ATemp"])
        collection = self.c.raw()
        # only 'owcowmet' returning
        assert len(collection) == 1        