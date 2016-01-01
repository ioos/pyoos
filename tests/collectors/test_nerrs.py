import pytz
import unittest
from datetime import datetime, timedelta
import pytest
from pyoos.collectors.nerrs.nerrs_soap import NerrsSoap


class NerrTest(unittest.TestCase):

    def setUp(self):
        self.c = NerrsSoap()

    @pytest.mark.xfail
    def test_list_nerrs_features(self):
        # The number of features may change... just make sure we get enough
        assert len(self.c.list_features()) > 10

    @pytest.mark.xfail
    def test_list_nerrs_variables(self):
        # The number of variables may change... just make sure we get enough
        assert len(self.c.list_variables()) > 10

        station_vars = self.c.list_variables(feature='rkbfbwq')
        assert station_vars == ['Depth', 'DO_mgl', 'DO_pct', 'pH', 'Sal', 'SpCond', 'Temp', 'Turb']

    @pytest.mark.xfail
    def test_nerrs_variable_filter(self):

        self.c.filter(features=['owcowmet', 'rkbfbwq'])
        self.c.filter(variables=["ATemp"])
        raw = self.c.raw()
        dsg = self.c.collect()
        # 'rkbfbwq' does not have ATemp, so it not returned
        assert len(raw) == 1
        assert sorted(map(lambda x: x.uid, dsg.elements)) == ['owcowmet']

        self.c.clear()
        self.c.filter(features=['owcowmet', 'rkbfbwq'])
        self.c.filter(variables=["ATemp", "Temp"])
        raw = self.c.raw()
        dsg = self.c.collect()
        # both are returned
        assert len(raw) == 2
        assert sorted(map(lambda x: x.uid, dsg.elements)) == ['owcowmet', 'rkbfbwq']

        # Must specify BBOX or Features subset for NERRS
        self.c.clear()
        self.c.filter(variables=["ATemp", "Temp"])
        with pytest.raises(ValueError):
            self.c.raw()

    @pytest.mark.xfail
    def test_nerrs_bbox_filter(self):

        self.c.filter(bbox=(85.0196, 29.6079, 85.089, 29.7791))
        raw = self.c.raw()
        dsg = self.c.collect()
        # Five features in the bounding box
        assert len(raw) == 5
        assert len(dsg.elements) == 5

    @pytest.mark.xfail
    def test_nerrs_feature_filter(self):

        self.c.filter(features=['owcowmet'])
        raw = self.c.raw()
        dsg = self.c.collect()
        assert len(raw) == 1
        assert sorted(map(lambda x: x.uid, dsg.elements)) == ['owcowmet']

        self.c.clear()
        self.c.filter(features=['owcowmet', 'rkbfbwq'])
        raw = self.c.raw()
        dsg = self.c.collect()
        # both are returned
        assert len(raw) == 2
        assert sorted(map(lambda x: x.uid, dsg.elements)) == ['owcowmet', 'rkbfbwq']

    @pytest.mark.xfail
    def test_nerrs_time_filter(self):

        self.c.filter(features=['owcowmet', 'rkbfbwq'])

        ending = datetime.utcnow() - timedelta(days=90)
        ending = ending.replace(tzinfo=pytz.utc)
        starting = ending - timedelta(hours=24)
        starting = starting.replace(tzinfo=pytz.utc)
        self.c.filter(start_time=starting, end_time=ending)
        raw = self.c.raw()
        dsg = self.c.collect()
        # both are returned
        assert len(raw) == 2
        sorted_stations = sorted(map(lambda x: x.uid, dsg.elements))
        assert sorted_stations == ['owcowmet', 'rkbfbwq']
        station = dsg.elements[0]
        station.calculate_bounds()
        assert sorted(station.time_range)[0] > starting - timedelta(hours=24)
        assert sorted(station.time_range)[0] < ending + timedelta(hours=24)
        assert sorted(station.time_range)[-1] > starting - timedelta(hours=24)
        assert sorted(station.time_range)[-1] < ending + timedelta(hours=24)

    @pytest.mark.xfail
    def test_nerrs_filter_chaining(self):

        # Test NERRS chaining
        self.c.filter(features=['owcowmet', 'rkbfbwq']).filter(variables=["ATemp"])
        raw = self.c.raw()
        dsg = self.c.collect()
        # only 'owcowmet' returning
        assert len(raw) == 1
        assert sorted(map(lambda x: x.uid, dsg.elements)) == ['owcowmet']

        # Test multiple filter types on one call to 'filter'
        self.c.clear()
        self.c.filter(features=['owcowmet', 'rkbfbwq'], variables=["ATemp"])
        raw = self.c.raw()
        dsg = self.c.collect()
        # only 'owcowmet' returning
        assert len(raw) == 1
        assert sorted(map(lambda x: x.uid, dsg.elements)) == ['owcowmet']
