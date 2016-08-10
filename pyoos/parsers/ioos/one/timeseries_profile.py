from __future__ import (absolute_import, division, print_function)

from dateutil import parser
from collections import OrderedDict, defaultdict
from bisect import bisect_left

from owslib.crs import Crs
from owslib.namespaces import Namespaces
from shapely.geometry import Point as sPoint

from paegan.cdm.dsg.member import Member
from paegan.cdm.dsg.features.station_profile import StationProfile
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.features.base.profile import Profile
from paegan.cdm.dsg.collections.base.profile_collection import ProfileCollection
from paegan.cdm.dsg.collections.station_collection import StationCollection

from owslib.swe.common import Time, DataChoice, DataRecord


def get_namespaces():
    ns = Namespaces()
    return ns.get_namespaces(["swe20"])
namespaces = get_namespaces()


class ProfileCache(object):
    """
    Helper class to accumulate observations and transform them into ProfileCollections representing TimeseriesProfiles.

    Used internally.
    """
    def __init__(self):
        self._cache = defaultdict(OrderedDict)

    def add_obs(self, sensor, t, obs_point, obs_members):
        """
        """
        profile = self._get_profile(sensor, t)
        point   = self._get_point(profile, obs_point)
        point.members.extend(obs_members)

    def get_collections(self):
        return {k[2] : ProfileCollection(elements=list(pd.values())) for k, pd in self._cache.items()}

    def _get_profile(self, sensor, t):
        sens_loc_tuple = (sensor['location']['point'].x, sensor['location']['point'].y, sensor['station'])
        profile_od     = self._cache[sens_loc_tuple]

        if t not in profile_od:
            profile          = Profile()
            profile.location = sPoint(*sens_loc_tuple[0:2])
            profile.time     = t

            # @TODO this is a hack until we can figure out how to assoc stations properly
            profile.station  = sensor['station']

            profile_od[t]    = profile
            return profile

        return profile_od[t]

    def _get_point(self, profile, point):
        """
        Finds the given point in the profile, or adds it in sorted z order.
        """
        cur_points_z = [p.location.z for p in profile.elements]
        try:
            cur_idx = cur_points_z.index(point.z)
            return profile.elements[cur_idx]
        except ValueError:
            new_idx            = bisect_left(cur_points_z, point.z)
            new_point          = Point()
            new_point.location = sPoint(point)
            new_point.time     = profile.time
            profile.elements.insert(new_idx, new_point)
            return new_point


class TimeSeriesProfile(object):
    def __init__(self, element):
        record = DataRecord(element)

        stations_field = record.get_by_name("stations")

        stations = {}
        sensors = {}

        for station in stations_field.content.field:
            s      = StationProfile()
            s.name = station.name
            s.uid  = station.content.get_by_name("stationID").content.value

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

            # sensors
            for sensor in station.content.get_by_name("sensors").content.field:
                name           = sensor.name
                uri            = sensor.content.get_by_name("sensorID").content.value

                sensors[name] = {'station'        : s.uid,
                                 'name'           : name,
                                 'uri'            : uri}
                # orientation
                ori_el = sensor.content.get_by_name("sensorOrientation")
                if ori_el:
                    orientation = self._parse_sensor_orientation(ori_el)
                    sensors[name]['sensor_orientation'] = orientation

                # location
                loc_el = sensor.content.get_by_name("sensorLocation")
                if loc_el:
                    location = self._parse_location(loc_el, s.location)
                    sensors[name]['location'] = location

                # profile bins
                profbins_el = sensor.content.get_by_name("profileBins")
                if profbins_el:
                    profile_bins = self._parse_profile_bins(profbins_el)
                    sensors[name]['profile_bins'] = profile_bins

                # OR profile heights
                profheights_el = sensor.content.get_by_name('profileHeights')
                if profheights_el:
                    profile_heights = self._parse_profile_heights(profheights_el)
                    sensors[name]['profile_heights'] = profile_heights

            s.sensors = sensors

            stations[s.uid] = s

        sensor_data = self._parse_sensor_data(record.get_by_name('observationData'), sensors)

        # sensor data is dict of station id -> profile collection
        for station_id, sensor_profile_data in sensor_data.items():
            stations[station_id].elements.extend(sensor_profile_data._elements)

        if len(stations) > 1:
            self.feature = StationCollection(elements=stations)
        elif len(stations) == 1:
            self.feature = next(iter(stations.values()))
        else:
            print("No stations found!")
            self.feature = None

    def _parse_sensor_orientation(self, ori_el):
        # 'srs':Crs(),    # @TODO (OWSLib cannot parse this Crs yet)
        orientation = {}
        for coord in ori_el.content.coordinate:
            orientation[coord.axisID] = {
                'name' : coord.name,
                'value' : coord.value,
                'axis' : coord.axisID,
                'uom' : coord.uom
            }

        return orientation

    def _parse_location(self, loc_el, station_point):
        vector         = loc_el.content

        srss           = vector.referenceFrame.split("&amp;")

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

        local_frame    = vector.localFrame
        lat            = vector.get_by_name("latitude").content.value
        lon            = vector.get_by_name("longitude").content.value
        z              = vector.get_by_name("height").content.value

        loc = [lon, lat]
        if z:
            loc.append(z)
        else:
            loc.append(station_point.z)

        location = {'horizontal_srs' : hsrs,
                    'vertical_srs'   : vsrs,
                    'localFrame'     : local_frame,
                    'point'          : sPoint(*loc)}

        return location

    def _parse_profile_bins(self, profbins_el):
        data_array = profbins_el.content
        count      = int(data_array.elementCount[0].text)
        data       = self._parse_data_array(data_array)

        bin_center_quantity = data_array.elementType.content.get_by_name('binCenter')
        bin_center = {'referenceFrame' : bin_center_quantity.content.referenceFrame,
                      'axisID'         : bin_center_quantity.content.axisID,
                      'uom'            : bin_center_quantity.content.uom,
                      'values'         : data[0]}

        bin_edges_quantityrange = data_array.elementType.content.get_by_name('binEdges')
        bin_edges = {'referenceFrame'  : bin_edges_quantityrange.content.referenceFrame,
                     'axisID'          : bin_edges_quantityrange.content.axisID,
                     'uom'             : bin_edges_quantityrange.content.uom,
                     'values'          : data[1]}

        profile_bins = {'bin_center': bin_center,
                        'bin_edges': bin_edges}

        return profile_bins

    def _parse_profile_heights(self, profheights_el):
        data_array = profheights_el.content
        count      = int(data_array.elementCount[0].text)
        data       = self._parse_data_array(data_array)

        height_el  = data_array.elementType.get_by_name('height')
        profile_definition = {'referenceFrame': height_el.content.referenceFrame,
                              'axisID'        : height_el.content.axisID,
                              'uom'           : height_el.content.uom,
                              'values'        : data[0]}

        return profile_definition

    def _parse_data_array(self, data_array):
        """
        Parses a general DataArray.
        """
        decimalSeparator    = data_array.encoding.decimalSeparator
        tokenSeparator      = data_array.encoding.tokenSeparator
        blockSeparator      = data_array.encoding.blockSeparator
        collapseWhiteSpaces = data_array.encoding.collapseWhiteSpaces

        data_values = data_array.values
        lines = [x for x in data_values.split(blockSeparator) if x != '']

        ret_val = []

        for row in lines:
            values = row.split(tokenSeparator)
            ret_val.append([float(v) if ' ' not in v.strip() else [float(vv) for vv in v.split()] for v in values])

        # transpose into columns
        return [list(x) for x in zip(*ret_val)]

    def _parse_sensor_data(self, obs_el, sensor_info):
        """
        Returns ProfileCollection
        """
        data_array = obs_el.content

        # get column defs
        data_record = data_array.elementType.content
        columns = []
        for f in data_record.field:
            columns.append(f)

        # get more information on sensor cols
        sensor_cols = defaultdict(list)
        sensor_vals = defaultdict(list)

        sensor_rec = data_record.get_by_name('sensor')
        for sendata in sensor_rec.content.item:
            if sendata.content is None:
                continue

            for f in sendata.content.field:
                sensor_cols[sendata.name].append(f)

        # @TODO deduplicate
        decimalSeparator    = data_array.encoding.decimalSeparator
        tokenSeparator      = data_array.encoding.tokenSeparator
        blockSeparator      = data_array.encoding.blockSeparator
        collapseWhiteSpaces = data_array.encoding.collapseWhiteSpaces

        data_values = data_array.values
        lines = [x for x in data_values.split(blockSeparator) if x != '']

        # profile cacher!
        profile_cache = ProfileCache()

        for row in lines:
            values = row.split(tokenSeparator)

            skey     = None
            i        = 0
            cur_time = None
            cur_qual = None

            for c in columns:

                if isinstance(c.content, Time) and c.content.definition == "http://www.opengis.net/def/property/OGC/0/SamplingTime":
                    cur_time = parser.parse(values[i])
                    i += 1

                    if len(c.quality):
                        # @TODO: do some quality constraint checks
                        i += len(c.quality)
                        # for qua in c.quality:

                elif isinstance(c.content, DataChoice) and c.name == "sensor":
                    sensor_key = values[i]
                    i += 1

                    sensor_dr = c.content.get_by_name(sensor_key).content
                    sensor_info_ = sensor_info[sensor_key]
                    parsed, nc = self._parse_sensor_record(sensor_dr, sensor_info_, values[i:])

                    # turn these into Points/Members
                    for rec in parsed:
                        # calc a Z value from rec/sensor and build point
                        point, members = self._build_obs_point(sensor_info_, rec)

                        # add to profile
                        profile_cache.add_obs(sensor_info_, cur_time, point, members)

                    i += nc

        return profile_cache.get_collections()

    def _parse_sensor_record(self, sensor_data_rec, sensor_info, rem_values):
        """
        Parses values via sensor data record passed in.
        Returns parsed values AND how many items it consumed out of rem_values.
        """
        val_idx = 0

        # @TODO seems there is only a single field in each of these
        assert len(sensor_data_rec.field) == 1
        sensor_data_array = sensor_data_rec.field[0].content

        # there is probably not going to be a count in the def, it'll be in the data
        count = None
        count_text = sensor_data_array.elementCount.text
        if count_text:
            count = int(count_text.strip())

        if not count:
            count = int(rem_values[val_idx])
            val_idx += 1

        parsed = []

        for recnum in range(count):
            cur  = []

            for f in sensor_data_array.elementType.field:
                cur_val = rem_values[val_idx]
                val_idx += 1

                m = Member(name=f.name,
                           standard=f.content.definition)

                if hasattr(f.content, 'uom'):
                    m['units'] = f.content.uom

                try:
                    m['value'] = float(cur_val)
                except ValueError:
                    m['value'] = cur_val

                if len(f.quality):
                    m['quality'] = []
                    for qual in f.quality:
                        cur_qual = rem_values[val_idx]
                        val_idx += 1

                        # @TODO check this against constraints
                        m['quality'].append(cur_qual)

                cur.append(m)

            parsed.append(cur)

        return parsed, val_idx

    def _build_obs_point(self, sensor_info, obs_recs):
        """
        Pulls bin/profile height info out and calcs a z.

        TODO: currently extremely naive

        Returns a 2-tuple: point, remaining obs_recs
        """
        cur_point = sensor_info['location']['point']

        keys = [m['name'] for m in obs_recs]
        if 'binIndex' in keys:
            zidx      = keys.index('binIndex')
            bin_index = int(obs_recs[zidx]['value'])
            z         = sensor_info['profile_heights']['values'][bin_index]

            point     = sPoint(cur_point.x, cur_point.y, cur_point.z + z)

        elif 'profileIndex' in keys:
            zidx      = keys.index('profileIndex')
            bin_index = int(obs_recs[zidx]['value'])

            # @TODO take into account orientation, may change x/y/z
            # @TODO bin edges?
            z         = sensor_info['profile_bins']['bin_center']['values'][bin_index]

            point     = sPoint(cur_point.x, cur_point.y, cur_point.z + z)

        else:
            raise ValueError("no binIndex or profileIndex in Member: %s", keys)

        # remove z related Member
        obs_recs = obs_recs[:]
        obs_recs.pop(zidx)

        return point, obs_recs
