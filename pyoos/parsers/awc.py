from __future__ import (absolute_import, division, print_function)

import pytz
from owslib.etree import etree

from shapely.geometry import Point as sPoint
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.features.station import Station as Station
from paegan.cdm.dsg.collections.station_collection import StationCollection
from paegan.cdm.dsg.member import Member
from datetime import datetime


class AwcToPaegan(object):
    def __init__(self, awc_list):
        for awc_data in awc_list:
            self._root = etree.fromstring(awc_data.encode())

            '''Code to get station iterator goes here.'''
            stations = []
            station_lookup = []
            times = []

            for metar in self._root.iter('METAR'):
                uid = metar.find("station_id").text
                if uid not in station_lookup:
                    s = Station()
                    s.uid = uid
                    vertical = metar.find("elevation_m").text
                    if vertical is None:
                        vertical = 0
                    s.location = sPoint(float(metar.find("latitude").text), float(metar.find("longitude").text), float(vertical))
                    s.set_property("metar_type", metar.find("metar_type").text)
                    s.set_property("horizontal_crs", "GCS")
                    s.set_property("vertical_units", "m")
                    s.set_property("vertical_crs", "AGL")

                    stations.append(s)
                    station_lookup.append(s.uid)
                    times.append({})
                else:
                    s = stations[station_lookup.index(uid)]

                variables = ["elevation_m", "raw_text", "temp_c", "dewpoint_c", "wind_dir_degrees", "wind_speed_kt", "visibility_statute_mi", "altim_in_hg", "wx_string", "sky_condition", "flight_category"]
                for variable in variables:
                    time_string = metar.find("observation_time").text
                    dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ")
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=pytz.utc)
                    dt = dt.astimezone(pytz.utc)

                    if dt not in list(times[station_lookup.index(s.uid)].keys()):
                        times[station_lookup.index(s.uid)][dt] = []

                    if metar.find(variable) != None:
                        if variable in set(["raw_text", "flight_category", "wx_string"]):
                            times[station_lookup.index(s.uid)][dt].append(Member(value=metar.find(variable).text, unit=None, name=variable, description=variable, standard=None))
                        elif variable == "sky_condition":
                            sky_condition = []
                            for cond in metar.findall(variable):
                                cover = cond.attrib["sky_cover"]
                                try:
                                    alt = cond.attrib["cloud_base_ft_agl"]
                                except:
                                    alt = None
                                sky_condition.append({"sky_cover" : cover, "cloud_base_ft_agl" : alt})
                            times[station_lookup.index(s.uid)][dt].append(Member(value=sky_condition, unit="ft_above_ground_level", name=variable, description=variable, standard=None))
                        else:
                            times[station_lookup.index(s.uid)][dt].append(Member(value=float(metar.find(variable).text), unit=variable.split("_")[-1], name=variable, description=variable, standard=None))

            for time_dict, station in zip(times, stations):
                for dts, members in time_dict.items():
                    p = Point()
                    p.time = dts
                    p.location = station.location
                    p.members = members
                    station.add_element(p)

        self.feature = StationCollection(elements=stations)
