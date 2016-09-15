from __future__ import (absolute_import, division, print_function)

from collections import defaultdict
from itertools import groupby
from dateutil.parser import parser
import time
import pytz

from paegan.cdm.dsg.member import Member
from paegan.cdm.dsg.features.station import Station
from paegan.cdm.dsg.collections.station_collection import StationCollection
from paegan.cdm.dsg.features.base.point import Point
from shapely.geometry import Point as sPoint
from numpy import nan as npNan


class HadsParser(object):

    def __init__(self):
        pass

    def parse(self, metadata, raw_data, var_filter, time_extents):

        self.parsed_metadata = self._parse_metadata(metadata)
        self.parsed_data     = self._parse_data(raw_data, var_filter, time_extents)
        self.feature         = self._build_station_collection(self.parsed_metadata, self.parsed_data)

        return self.feature

    def _build_station_collection(self, parsed_metadata, parsed_data):

        stations = []
        for station_code, station_metadata in parsed_metadata.items():
            s = Station()
            s.uid = station_code
            s.name = station_metadata['nwsli']
            s.location = sPoint(station_metadata['longitude'],
                                station_metadata['latitude'],
                                0)  # hads always vertically zero

            s.set_property("location_description" , station_metadata['location_text'])
            s.set_property("state"                , station_metadata['state'])
            s.set_property("country"              , "USA")   # @TODO
            s.set_property("vertical_units"       , "ft")
            s.set_property("horizontal_crs"       , "EPSG:4326")
            s.set_property("vertical_crs"         , None)
            s.set_property("hsa"                  , station_metadata['hsa'])
            s.set_property("init_transmit"        , station_metadata['init_transmit'])
            s.set_property("manufacturer"         , station_metadata['manufacturer'])
            s.set_property("owner"                , station_metadata['owner'])
            s.set_property("channel"              , station_metadata['channel'])

            stations.append(s)

            # data

            # possibility no data for this station, or vars filtered all out
            if station_code not in parsed_data:
                continue

            # need to group into distinct time/z value pairs

            # create a keyfunc (creates string of <z>-<timestamp>)
            zandtime = lambda x: str(x[3]) + "-" + str(time.mktime(x[1].timetuple()))

            # annotate data with z values, sort, group by keyfunc (z/time)
            grouped_data = groupby(sorted([(x[0],
                                            x[1],
                                            x[2],
                                            parsed_metadata[station_code]['variables'][x[0]]['base_elevation']) for
            x in parsed_data[station_code]], key=zandtime), zandtime)

            for _, group in grouped_data:

                # group is an iterator, turn it into a list (it will have at least one item)
                groupvals = list(group)

                p = Point()
                p.time = groupvals[0][1]
                p.location = sPoint(station_metadata['longitude'],
                                    station_metadata['latitude'],
                                    groupvals[0][3])

                for val in groupvals:
                    std_var = self.get_variable_info(val[0])
                    if std_var is None:
                        print("Unknown PE Code, ignoring: {} (station: {}).".format(val[0], station_code))
                        continue

                    p.add_member(Member(value=val[2],
                                        standard=std_var[0],
                                        unit=std_var[1],
                                        name=std_var[2],
                                        description=std_var[3]))

                s.add_element(p)

        return StationCollection(elements=stations)

    def _parse_data(self, raw_data, var_filter, time_extents):
        """
        Transforms raw HADS observations into a dict:
            station code -> [(variable, time, value), ...]

        Takes into account the var filter (if set).
        """

        retval = defaultdict(list)
        p = parser()

        begin_time, end_time = time_extents

        for line in raw_data.splitlines():
            if len(line) == 0:
                continue

            fields = line.split("|")[0:-1]
            if var_filter is None or fields[2] in var_filter:
                dt = p.parse(fields[3]).replace(tzinfo=pytz.utc)
                if (begin_time is None or dt >= begin_time) and (end_time is None or dt <= end_time):
                    try:
                        value = float(fields[4]) if fields[4] != 'NaN' else npNan
                    except ValueError:
                        value = npNan
                    retval[fields[0]].append((fields[2], dt, value))

        return dict(retval)

    def _parse_metadata(self, metadata):
        """
        Transforms raw HADS metadata into a dictionary (station code -> props)
        """
        retval = {}

        # these are the first keys, afterwards follows a var-len list of variables/props
        # first key always blank so skip it
        field_keys = ['nesdis_id',
                      'nwsli',
                      'location_text',
                      'latitude',
                      'longitude',
                      'hsa',
                      'state',
                      'owner',
                      'manufacturer',
                      'channel',
                      'init_transmit',  # HHMM
                      'trans_interval']  # min

        # repeat in blocks of 7 after field_keys
        var_keys = ['pe_code',
                    'data_interval',  # min
                    'coefficient',
                    'constant',
                    'time_offset',  # min
                    'base_elevation',  # ft
                    'gauge_correction']  # ft

        lines = metadata.splitlines()
        for line in lines:
            if len(line) == 0:
                continue

            raw_fields = line.split("|")

            fields = dict(zip(field_keys, raw_fields[1:len(field_keys)]))

            # how many blocks of var_keys after initial fields
            var_offset = len(field_keys) + 1
            var_blocks = (len(raw_fields) - var_offset) // len(var_keys)     # how many variables
            vars_only  = raw_fields[var_offset:]
            variables  = {}

            for offset in range(var_blocks):
                var_dict = dict(zip(var_keys, vars_only[offset*len(var_keys):(offset+1)*len(var_keys)]))
                variables[var_dict['pe_code']] = var_dict

                var_dict['base_elevation'] = float(var_dict['base_elevation'])
                var_dict['gauge_correction'] = float(var_dict['gauge_correction'])
                del var_dict['pe_code']  # no need to duplicate

            line_val = {'variables' : variables}
            line_val.update(fields)

            # conversions
            def dms_to_dd(dms):
                parts = dms.split(" ")
                sec   = int(parts[1]) * 60 + int(parts[2])
                return float(parts[0]) + (sec / 3600.0)  # negative already in first portion

            line_val['latitude']  = dms_to_dd(line_val['latitude'])
            line_val['longitude'] = dms_to_dd(line_val['longitude'])

            retval[line_val['nesdis_id']] = line_val

        return retval

    @classmethod
    def get_variable_info(cls, hads_var_name):
        """
        Returns a tuple of (mmi name, units, english name, english description) or None.
        """
        if hads_var_name == "UR":
            return ("wind_gust_from_direction", "degrees from N", "Wind Gust from Direction", "Direction from which wind gust is blowing when maximum wind speed is observed.  Meteorological Convention. Wind is motion of air relative to the surface of the earth.")
        elif hads_var_name in ["VJA", "TX"]:
            return ("air_temperature_maximum", "f", "Air Temperature Maximum", "")
        elif hads_var_name in ["VJB", "TN"]:
            return ("air_temperature_minimum", "f", "Air Temperature Minumum", "")
        elif hads_var_name == "PC":  # PC2?
            return ("precipitation_accumulated", "in", "Precipitation Accumulated", "Amount of liquid equivalent precipitation accumulated or totaled for a defined period of time, usually hourly, daily, or annually.")
        elif hads_var_name == "PP":
            return ("precipitation_rate", "in", "Precipitation Rate", "Amount of wet equivalent precipitation per unit time.")
        elif hads_var_name == "US":
            return ("wind_speed", "mph", "Wind Speed", "Magnitude of wind velocity. Wind is motion of air relative to the surface of the earth.")
        elif hads_var_name == "UD":
            return ("wind_from_direction", "degrees_true", "Wind from Direction", "Direction from which wind is blowing.  Meteorological Convention. Wind is motion of air relative to the surface of the earth.")
        elif hads_var_name in ["UP", "UG", "VUP"]:
            return ("wind_gust", "mph", "Wind Gust Speed", "Maximum instantaneous wind speed (usually no more than but not limited to 10 seconds) within a sample averaging interval. Wind is motion of air relative to the surface of the earth.")
        elif hads_var_name in ["TA", "TA2"]:
            return ("air_temperature", "f", "Air Temperature", "Air temperature is the bulk temperature of the air, not the surface (skin) temperature.")
        elif hads_var_name == "MT":
            return ("fuel_temperature", "f", "Fuel Temperature", "")
        elif hads_var_name == "XR":
            return ("relative_humidity", "percent", "Relative Humidity", "")
        elif hads_var_name == "VB":
            return ("battery_voltage", "voltage", "Battery Voltage", "")
        elif hads_var_name == "MM":
            return ("fuel_moisture", "percent", "Fuel Moisture", "")
        elif hads_var_name == "RW":
            return ("solar_radiation", "watt/m^2", "Solar Radiation", "")
        elif hads_var_name == "RS":
            return ("photosynthetically_active_radiation", "watt/m^2", "Photosynthetically Active Radiation", "")
        elif hads_var_name == "TW":     # TW2?
            return ("sea_water_temperature", "f", "Sea Water Temperature", "Sea water temperature is the in situ temperature of the sea water.")
        elif hads_var_name == "WT":
            return ("turbidity", "nephelometric turbidity units", "Turbidity", "")
        elif hads_var_name == "WC":
            return ("sea_water_electrical_conductivity", "micro mhos/cm", "Sea Water Electrical Conductivity", "")
        elif hads_var_name == "WP":
            return ("sea_water_ph_reported_on_total_scale", "std units", "Sea Water PH reported on Total Scale", "the measure of acidity of seawater")
        elif hads_var_name == "WO":
            return ("dissolved_oxygen", "ppm", "Dissolved Oxygen", "")
        elif hads_var_name == "WX":
            return ("dissolved_oxygen_saturation", "percent", "Dissolved Oxygen Saturation", "")
        elif hads_var_name == "TD":
            return ("dew_point_temperature", "f", "Dew Point Temperature", "the temperature at which a parcel of air reaches saturation upon being cooled at constant pressure and specific humidity.")
        elif hads_var_name == "HG":  # HG2?
            return ("stream_gage_height", "ft", "Stream Gage Height", "")
        elif hads_var_name == "HP":
            return ("water_surface_height_above_reference_datum", "ft", "Water Surface Height Above Reference Datum", "means the height of the upper surface of a body of liquid water, such as sea, lake or river, above an arbitrary reference datum.")
        elif hads_var_name == "WS":
            return ("salinity", "ppt", "Salinity", "")
        elif hads_var_name == "HM":
            return ("water_level", "ft", "Water Level", "")
        elif hads_var_name == "PA":
            return ("air_pressure", "hp", "Air Pressure", "")
        elif hads_var_name == "SD":
            return ("snow_depth", "in", "Snow Depth", "")
        elif hads_var_name == "SW":
            return ("snow_water_equivalent", "m", "Snow Water Equivalent", "")
        elif hads_var_name == "TS":
            return ("soil_temperature", "f", "Soil Temperature", "Soil temperature is the bulk temperature of the soil, not the surface (skin) temperature.")

        return None
