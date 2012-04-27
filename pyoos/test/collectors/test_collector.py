import unittest
from pyoos.collectors.collector import Collector
from datetime import datetime

from pytz import timezone
from pytz.reference import Eastern

class CollectorTest(unittest.TestCase):
    def test_times_return_utc(self):
        c = Collector()

        # Assumes timezones without a timezone are UTC
        c.start_time = datetime(2000,2,1,10)
        c.end_time = datetime(2000,2,3,8)
        assert c.start_time == datetime(2000,2,1,10, tzinfo=timezone('UTC'))
        assert c.end_time == datetime(2000,2,3,8, tzinfo=timezone('UTC'))

        # Always returns UTC (5 hour difference here)
        c.start_time = datetime(2000,2,1,10, tzinfo=Eastern)
        c.end_time = datetime(2000,2,3,8, tzinfo=Eastern)
        assert c.start_time == datetime(2000,2,1,15, tzinfo=timezone('UTC'))
        assert c.end_time == datetime(2000,2,3,13, tzinfo=timezone('UTC'))
