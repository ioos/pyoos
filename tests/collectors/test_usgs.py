import unittest
from pyoos.collectors.usgs.usgs_rest import UsgsRest
from datetime import datetime, timedelta


class USGSTest(unittest.TestCase):

    def setUp(self):
        self.c = UsgsRest()

    def test_by_bbox(self):
        self.c.filter(bbox=(-87, 46, -85, 48))
        collection = self.c.collect()
        collection.calculate_bounds()

        # Returns 4 stations: 04044724, 04045500, 04046000, 04056500
        assert len(collection.elements) == 4
        assert sorted(map(lambda x: x.uid, collection.elements)) == ["04044724", "04045500", "04046000", "04056500"]

        station = collection.elements[0]
        assert station.name == "AU TRAIN RIVER AT FOREST LAKE, MI"
        # Measures 2 variables
        assert len(station.get_unique_members()) == 2
        assert station.location.x == -86.8501514
        assert station.location.y == 46.34077908
        assert station.location.z == 0

        # Apply time filter as well
        starting = datetime(2013, 12, 31, 0, 0, 0)
        ending = starting + timedelta(hours=6)
        self.c.filter(start=starting, end=ending)
        collection = self.c.collect()
        collection.calculate_bounds()

        # Returns 4 stations: 04044724, 04045500, 04046000, 04056500
        assert len(collection.elements) == 4
        assert sorted(map(lambda x: x.uid, collection.elements)) == ["04044724", "04045500", "04046000", "04056500"]

    def test_by_state(self):
        # Clear filters
        self.c.clear()
        # Add custom state filter
        self.c.filter(state="ri")
        collection = self.c.collect()

        # Returns 43 stations.
        # FIXME: This is a flaky test.  The station number changed from
        #41, to 42 and now 43. (And back to 42!)
        assert len(collection.elements) == 42

        station = collection.elements[0]
        assert station.name == "TEN MILE R., PAWTUCKET AVE. AT E. PROVIDENCE, RI"
        # Measures 2 variables
        assert len(station.get_unique_members()) == 2
        assert station.location.x == -71.3511649
        assert station.location.y == 41.83093376
        assert station.location.z == 0

    def test_by_site_code(self):
        # Clear filters
        self.c.clear()
        # Add custom state filter
        self.c.filter(features=['04001000'])
        collection = self.c.collect()
        collection.calculate_bounds()

        station = collection.elements[0]
        assert station.uid == '04001000'
        assert station.name == 'WASHINGTON CREEK AT WINDIGO, MI'
        assert station.location.x == -89.1459196999999932
        assert station.location.y == 47.9212792000000007
        assert station.location.z == 0
