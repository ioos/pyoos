from __future__ import (absolute_import, division, print_function)

import pytz
from owslib.etree import ElementType, etree

from owslib.waterml.wml11 import WaterML_1_1
from shapely.geometry import Point as sPoint
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.features.station import Station as Station
from paegan.cdm.dsg.collections.station_collection import StationCollection
from paegan.cdm.dsg.member import Member


class WaterML11ToPaegan(object):
    def __init__(self, waterml_data):

        if isinstance(waterml_data, ElementType):
            self._root = waterml_data
        else:
            self._root = etree.fromstring(waterml_data.encode())

        response = WaterML_1_1(self._root).response

        stations = []
        station_lookup = []

        for timeseries in response.time_series:
            station_code = sorted(timeseries.source_info.site_codes)[0]
            # Create station if we have not seen it
            if station_code not in station_lookup:
                s = Station()
                s.uid = station_code

                info = timeseries.source_info
                s.name = info.site_name
                s.set_property("station_type", info.site_types)
                s.set_property("huc", info.site_properties.get("hucCd"))
                s.set_property("county", info.site_properties.get("countyCd"))
                s.set_property("state", info.site_properties.get("stateCd"))

                # Now set the station's location
                vertical = info.elevation
                if vertical is None:
                    vertical = 0

                try:
                    location = info.location.geo_coords[0]
                    srs = info.location.srs[0]
                except:
                    print("Could not find a location for {}... skipping station".format(s.uid))
                    continue

                s.location = sPoint(float(location[0]), float(location[1]), vertical)
                s.set_property("horizontal_crs", srs)
                s.set_property("vertical_units", "m")
                s.set_property("vertical_crs", info.vertical_datum)
                s.set_property("location_description", info.location.notes)

                stations.append(s)
                station_lookup.append(s.uid)

            times = {}
            variable = timeseries.variable
            for variable_timeseries in timeseries.values:
                for r in variable_timeseries:
                    dt = r.date_time
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=pytz.utc)
                    dt = dt.astimezone(pytz.utc)

                    if dt not in times.keys():
                        times[dt] = []

                    times[dt].append(Member(value=r.value, unit=variable.unit.code, name=variable.variable_name, description=variable.variable_description, standard=variable.variable_code))

            station = stations[station_lookup.index(station_code)]
            for dts, members in times.items():
                p = Point()
                p.time = dts
                p.location = station.location
                p.members = members
                station.add_element(p)

        self.feature = StationCollection(elements=stations)
