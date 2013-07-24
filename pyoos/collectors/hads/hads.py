import os.path
import re
import requests
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

    def clear(self):
        super(Hads, self).clear()

        self.station_codes      = None

    def list_variables(self):
        station_codes = self._get_station_codes()
        return self._list_variables(station_codes)

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

        map(variables.add, rvar.findall(resp.text))
        return variables

    def list_features(self):
        return self._get_station_codes()

    def collect(self):
        raw_data = self.raw()
        return map(HadsParser, raw_data)

    def raw(self, format=None):
        """
        Returns a tuple of (metadata, raw data)
        """
        station_codes = self._get_station_codes()
        metadata = self._get_metadata(station_codes)

        return (metadata, self._get_raw_data(station_codes))

    def _get_metadata(self, station_codes):
        resp = requests.post(self.metadata_url, data={'state' : 'nil',
                                                      'hsa'   : 'nil',
                                                      'of'    : '1',
                                                      'extraids' : " ".join(station_codes),
                                                      'data' : "Get Meta Data"})
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

        # @TODO: filter by bounding box against a shapefile
        state_matches = None

        if self.bbox:
            with collection(os.path.join("resources", "ne_50m_admin_1_states_provinces_lakes_shp.shp"), "r") as c:
                geom_matches = map(lambda x: x['properties'], c.filter(bbox=self.bbox))
                state_matches = map(lambda x: x['postal'], filter(lambda x: x['admin'] != u'Canada', geom_matches))

        self.station_codes = []

        for state_url in state_urls:
            if state_matches is not None:
                state_abbr = state_url.split("/")[-1].split(".")[0]
                if state_abbr not in state_matches:
                    continue

            self.station_codes.extend(self._get_stations_for_state(state_url))

        return self.station_codes

    def _get_state_urls(self):
        root = BeautifulSoup(requests.get(self.states_url).text)
        areas = root.find_all("area")
        return list(set(map(lambda x: x.attrs.get('href', None), areas)))

    def _get_stations_for_state(self, state_url):
        #print state_url
        state_root = BeautifulSoup(requests.get(state_url).text)
        return filter(lambda x: len(x) > 0, map(lambda x: x.attrs['href'].split("nesdis_id=")[-1], state_root.find_all('a')))

    def _get_raw_data(self, station_codes):
        resp = requests.post(self.obs_retrieval_url, data={'state' : 'nil',
                                                           'hsa'   : 'nil',
                                                           'of'    : '1',
                                                           'extraids' : " ".join(station_codes),
                                                           'sinceday' : -1})     # @TODO
        resp.raise_for_status()

        return resp.text

