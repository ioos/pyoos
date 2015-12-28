from __future__ import (absolute_import, division, print_function)

from dateutil import parser
from copy import copy

from owslib.crs import Crs
from owslib.util import nspath_eval
from owslib.namespaces import Namespaces
from shapely.geometry import Point as sPoint

from paegan.cdm.dsg.member import Member
from paegan.cdm.dsg.features.station import Station
from paegan.cdm.dsg.collections.station_collection import StationCollection
from paegan.cdm.dsg.features.base.point import Point

from owslib.swe.common import Time, DataChoice, DataRecord, AbstractSimpleComponent


def get_namespaces():
    ns = Namespaces()
    return ns.get_namespaces(["swe20"])
namespaces = get_namespaces()


def nspv(path):
    return nspath_eval(path, namespaces)


class TimeSeries(object):
    def __init__(self, element):

        record = DataRecord(element)

        # Top level org structure
        stations_field = record.get_by_name("stations")
        stations = {}
        sensors = {}
        for station in stations_field.content.field:
            s = Station()
            s.name  = station.name
            s.uid   = station.content.get_by_name("stationID").content.value

            # Location
            vector  = station.content.get_by_name("platformLocation").content
            srss = vector.referenceFrame.split("&amp;")
            hsrs = None
            try:
                hsrs = Crs(srss[0])
            except ValueError:
                pass

            vsrs = None
            try:
                vsrs = Crs(srss[-1].replace("2=http:", "http:"))
            except ValueError:
                pass

            s.set_property("horizontal_srs", hsrs)
            s.set_property("vertical_srs",   vsrs)
            s.set_property("localFrame",     vector.localFrame)

            lat = vector.get_by_name("latitude").content.value
            lon = vector.get_by_name("longitude").content.value
            z   = vector.get_by_name("height").content.value

            loc = [lon, lat]
            if z:
                loc.append(z)

            s.location = sPoint(*loc)

            # Sensors
            for sensor in station.content.get_by_name("sensors").content.field:
                name        = sensor.name
                uri         = sensor.content.get_by_name("sensorID").content.value
                height      = None
                location_quantity = sensor.content.get_by_name("height").content
                if location_quantity.referenceFrame == "#%s_frame" % s.name:
                    # Uses the station as reference frame
                    if location_quantity.value and z:
                        height      = z + location_quantity.value
                    horizontal_srs  = s.get_property("horizontal_srs")
                    vertical_srs    = s.get_property("vertical_srs")
                else:
                    # Uses its own height
                    if location_quantity.value:
                        height      = location_quantity.value
                    horizontal_srs  = None
                    vertical_srs    = None
                    if hasattr(sensor, 'referenceFrame'):
                        srss            = sensor.referenceFrame.split("&amp;")
                        try:
                            horizontal_srs = Crs(srss[0])
                        except ValueError:
                            pass
                        try:
                            vertical_srs = Crs(srss[-1].replace("2=http:", "http:"))
                        except ValueError:
                            pass

                loc = [s.location.x, s.location.y]
                if height:
                    loc.append(height)

                location            = sPoint(*loc)

                sensors[name] = {   'station'           : s.uid,
                                    'name'              : name,
                                    'uri'               : uri,
                                    'horizontal_srs'    : horizontal_srs,
                                    'vertical_srs'      : vertical_srs,
                                    'location'          : location,
                                    'columns'           : [],  # Array of Members representing the columns
                                    'values'            : []   # Array of Points (the actual data)
                                }

            stations[s.uid] = s

        # Start building the column structure
        data_array = record.get_by_name("observationData").content
        data_record = data_array.elementType.content

        columns = []
        # Data outside of the <field name="sensors"> DataChoice element
        for f in data_record.field:
            columns.append(f)

        # Data inside of DataChoice
        sensor_data = data_record.get_by_name("sensor")
        for sendata in sensor_data.content.item:
            if sendata.content is not None:
                sensors[sendata.name]['columns'] = []
                sensors[sendata.name]['values'] = []
                for f in sendata.content.field:
                    # Create a model Member for each column that will be copied and filled with data from each row
                    sensors[sendata.name]['columns'].append(f)

        decimalSeparator    = data_array.encoding.decimalSeparator
        tokenSeparator      = data_array.encoding.tokenSeparator
        blockSeparator      = data_array.encoding.blockSeparator
        collapseWhiteSpaces = data_array.encoding.collapseWhiteSpaces

        data_values = data_array.values
        self.raw_data = copy(data_values)

        for row in [x for x in data_values.split(blockSeparator) if x != ""]:

            pt = None
            members     = []
            values      = row.split(tokenSeparator)
            sensor_key  = None
            i           = 0

            for x in columns:

                if isinstance(x.content, Time) and x.content.definition == "http://www.opengis.net/def/property/OGC/0/SamplingTime":
                    pt      = Point()
                    pt.time = parser.parse(values[i])

                elif isinstance(x.content, DataChoice):
                    sensor_key = values[i]
                    dc_cols = sensors[sensor_key]['columns']

                    for j, c in enumerate(dc_cols):
                        if isinstance(c.content, AbstractSimpleComponent):
                            m = Member( units=c.content.uom,
                                        name=c.name,
                                        standard=c.content.definition,
                                        value=float(values[i+1]))
                            members.append(m)

                        elif isinstance(c.content, Time) and c.content.definition == "http://www.opengis.net/def/property/OGC/0/SamplingTime":
                            pt      = Point()
                            pt.time = parser.parse(values[i])

                        # For each data column
                        i += 1

                elif isinstance(x.content, AbstractSimpleComponent):
                    m = Member( units=x.content.uom,
                                name=x.name,
                                standard=x.content.definition,
                                value=float(values[i]))
                    members.append(m)

                else:
                    print("WHAT AM I?")

                i += 1

            pt.members = members
            pt.location = stations[sensors[sensor_key]['station']].location
            sensors[sensor_key]['values'].append(pt)

        for k, v in stations.items():
            for sk, sv in sensors.items():
                # Match on station uid
                if sv['station'] == k:
                    v.elements = self._merge_points(v.elements or [], sv['values'])

        if len(stations) > 1:
            self.feature = StationCollection(elements=stations)
        elif len(stations) == 1:
            self.feature = next(iter(stations.values()))
        else:
            print("No stations found!")

    def _merge_points(self, pc1, pc2):
        """
        Merges points based on time/location.

        @TODO: move to paegan, SO SLOW
        """
        res = pc1[:]

        for p in pc2:
            for sp in res:
                if sp.time == p.time and (sp.location is None or (sp.location.equals(p.location))):
                    sp.members.extend(p.members)
                    break
            else:
                res.append(p)

        return res

