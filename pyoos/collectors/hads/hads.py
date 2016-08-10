from __future__ import (absolute_import, division, print_function)

import os.path
import re
import requests
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
from fiona import collection

from pyoos.parsers.hads import HadsParser
from pyoos.collectors.collector import Collector


class Hads(Collector):
    def __init__(self, **kwargs):
        super(Hads, self).__init__()

        self.states_url         = kwargs.get('states_url', "http://amazon.nws.noaa.gov/hads/goog_earth/")
        self.metadata_url       = kwargs.get('metadata_url',  "http://amazon.nws.noaa.gov/nexhads2/servlet/DCPInfo")
        self.obs_retrieval_url  = kwargs.get('obs_retrieval_url', "http://amazon.nws.noaa.gov/nexhads2/servlet/DecodedData")

        self.station_codes      = None
        self.parser             = HadsParser()

    def clear(self):
        super(Hads, self).clear()

        self.station_codes      = None

    @Collector.bbox.setter
    def bbox(self, bbox):
        Collector.bbox.fset(self, bbox)
        self.station_codes      = None

    @Collector.features.setter
    def features(self, features):
        Collector.features.fset(self, features)
        self.station_codes      = None

    def list_variables(self):
        """
        List available variables and applies any filters.
        """
        station_codes = self._get_station_codes()
        station_codes = self._apply_features_filter(station_codes)
        variables = self._list_variables(station_codes)

        if hasattr(self, '_variables') and self.variables is not None:
            variables.intersection_update(set(self.variables))

        return list(variables)

    def _list_variables(self, station_codes):
        """
        Internal helper to list the variables for the given station codes.
        """
        # sample output from obs retrieval:
        #
        # DD9452D0
        #     HP(SRBM5)
        #         2013-07-22 19:30 45.97
        #     HT(SRBM5)
        #         2013-07-22 19:30 44.29
        #     PC(SRBM5)
        #         2013-07-22 19:30 36.19
        #
        rvar = re.compile("""\n\s([A-Z]{2}[A-Z0-9]{0,1})\(\w+\)""")

        variables = set()
        resp = requests.post(self.obs_retrieval_url, data={'state' : 'nil',
                                                           'hsa'   : 'nil',
                                                           'of'    : '3',
                                                           'extraids' : " ".join(station_codes),
                                                           'sinceday' : -1})
        resp.raise_for_status()

        list(map(variables.add, rvar.findall(resp.text)))
        return variables

    def list_features(self):
        station_codes = self._get_station_codes()
        station_codes = self._apply_features_filter(station_codes)

        return station_codes

    def collect(self):
        var_filter = None
        if hasattr(self, '_variables'):
            var_filter = self._variables

        time_extents = (self.start_time if hasattr(self, 'start_time') else None, self.end_time if hasattr(self, 'end_time') else None)

        metadata, raw_data = self.raw()
        return self.parser.parse(metadata, raw_data, var_filter, time_extents)

    def raw(self, format=None):
        """
        Returns a tuple of (metadata, raw data)
        """
        station_codes = self._apply_features_filter(self._get_station_codes())
        metadata      = self._get_metadata(station_codes)
        raw_data      = self._get_raw_data(station_codes)

        return (metadata, raw_data)

    def _apply_features_filter(self, station_codes):
        """
        If the features filter is set, this will return the intersection of
        those filter items and the given station codes.
        """
        # apply features filter
        if hasattr(self, 'features') and self.features is not None:
            station_codes = set(station_codes)
            station_codes = list(station_codes.intersection(set(self.features)))

        return station_codes

    def _get_metadata(self, station_codes):
        resp = requests.post(self.metadata_url, data={'state'    : 'nil',
                                                      'hsa'      : 'nil',
                                                      'of'       : '1',
                                                      'extraids' : " ".join(station_codes),
                                                      'data'     : "Get Meta Data"})
        resp.raise_for_status()
        return resp.text

    def _get_station_codes(self, force=False):
        """
        Gets and caches a list of station codes optionally within a bbox.

        Will return the cached version if it exists unless force is True.
        """
        if not force and self.station_codes is not None:
            return self.station_codes

        state_urls = self._get_state_urls()

        # filter by bounding box against a shapefile
        state_matches = None

        if self.bbox:
            with collection(os.path.join("resources", "ne_50m_admin_1_states_provinces_lakes_shp.shp"), "r") as c:
                geom_matches = [x['properties'] for x in c.filter(bbox=self.bbox)]
                state_matches = [x['postal'] if x['admin'] != 'Canada' else 'CN' for x in geom_matches]

        self.station_codes = []

        for state_url in state_urls:
            if state_matches is not None:
                state_abbr = state_url.split("/")[-1].split(".")[0]
                if state_abbr not in state_matches:
                    continue

            self.station_codes.extend(self._get_stations_for_state(state_url))

        if self.bbox:
            # retreive metadata for all stations to properly filter them
            metadata        = self._get_metadata(self.station_codes)
            parsed_metadata = self.parser._parse_metadata(metadata)

            def in_bbox(code):
                lat = parsed_metadata[code]['latitude']
                lon = parsed_metadata[code]['longitude']

                return lon >= self.bbox[0] and lon <= self.bbox[2] and lat >= self.bbox[1] and lat <= self.bbox[3]

            self.station_codes = list(filter(in_bbox, self.station_codes))

        return self.station_codes

    def _get_state_urls(self):
        root = BeautifulSoup(requests.get(self.states_url).text)
        areas = root.find_all("area")
        return list(set([x.attrs.get('href', None) for x in areas]))

    def _get_stations_for_state(self, state_url):
        state_root = BeautifulSoup(requests.get(state_url).text)
        return [x for x in [x.attrs['href'].split("nesdis_id=")[-1] for x in state_root.find_all('a')] if len(x) > 0]

    def _get_raw_data(self, station_codes):
        since = 7
        if hasattr(self, 'start_time') and self.start_time is not None:
            # calc delta between now and start_time
            timediff = datetime.utcnow().replace(tzinfo=pytz.utc) - self.start_time

            if timediff.days == 0:
                if timediff.seconds / 60 / 60 > 0:
                    since = -(timediff.seconds / 60 / 60)
                elif timediff.seconds / 60 > 0:
                    since = -1  # 1 hour minimum resolution
            else:
                since = min(7, timediff.days)       # max of 7 days

        resp = requests.post(self.obs_retrieval_url, data={'state'    : 'nil',
                                                           'hsa'      : 'nil',
                                                           'of'       : '1',
                                                           'extraids' : " ".join(station_codes),
                                                           'sinceday' : since})
        resp.raise_for_status()

        return resp.text
