from __future__ import (absolute_import, division, print_function)

import unittest
from pyoos.collectors.collector import Collector
from datetime import datetime

from pytz import timezone
from pytz.reference import Eastern


class CollectorTest(unittest.TestCase):
    def test_times_return_utc(self):
        c = Collector()

        # Assumes timezones without a timezone are UTC
        c.filter(start=datetime(2000, 2, 1, 10), end=datetime(2000, 2, 3, 8))
        assert c._start_time == datetime(2000, 2, 1, 10, tzinfo=timezone('UTC'))
        assert c._end_time == datetime(2000, 2, 3, 8, tzinfo=timezone('UTC'))

        # Always returns UTC (5 hour difference here)
        c.filter(start=datetime(2000, 2, 1, 10, tzinfo=Eastern), end=datetime(2000, 2, 3, 8, tzinfo=Eastern))
        assert c._start_time == datetime(2000, 2, 1, 15, tzinfo=timezone('UTC'))
        assert c._end_time == datetime(2000, 2, 3, 13, tzinfo=timezone('UTC'))
