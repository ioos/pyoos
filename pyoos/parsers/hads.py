from collections import defaultdict

from paegan.cdm.dsg.member import Member
from paegan.cdm.dsg.features.station import Station
from paegan.cdm.dsg.collections.station_collection import StationCollection
from paegan.cdm.dsg.features.base.point import Point
from shapely.geometry import Point as sPoint

class HadsParser(object):
    def __init__(self, metadata, raw_data):

        self.parsed_metadata = self._parse_metadata(metadata)
        self.parsed_data     = self._parse_data(raw_data)
        self.feature = self._build_station_collection(self.parsed_metadata, self.parsed_data)

    def _build_station_collection(self, parsed_metadata, parsed_data):

        stations = []
        for station_code, station_metadata in parsed_metadata.iteritems():
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

            # data
            assert station_code in parsed_data

            for variable_name, data in parsed_data[station_code].iteritems():
                assert variable_name in station_metadata['variables']

                p = Point()
                #p.time = start_time # @TODO: init_transmit?
                p.location = sPoint(station_metadata['longitude'],
                                    station_metadata['latitude'],
                                    float(station_metadata['variables'][variable_name]['base_elevation']))

                for val in data:
                    p.add_member(Member(value=val[1],
                                        unit='',    # @TODO
                                        name=variable_name,
                                        description='', # @TODO
                                        time=val[0]))

                s.add_element(p)

            stations.append(s)

        return StationCollection(elements=stations)

    def _parse_data(self, raw_data):
        """
        Transforms raw HADS observations into a dict/dict/list format:
            Station Code
                PE Code (variable)
                    [measurement 1, measurement 2..]
                PE Code 2
                    [measurement 1]
            Station Code 2
        """

        retval = defaultdict(lambda : defaultdict(list))

        for line in raw_data.splitlines():
            if len(line) == 0:
                continue

            fields = line.split("|")[0:-1]
            retval[fields[0]][fields[2]].append((fields[3], fields[4]))

        return retval

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
                      'init_transmit', # HHMM
                      'trans_interval'] #min

        # repeat in blocks of 7 after field_keys
        var_keys = ['pe_code',
                    'data_interval', #min
                    'coefficient',
                    'constant',
                    'time_offset', #min
                    'base_elevation', #ft
                    'gauge_correction'] #ft

        lines = metadata.splitlines()
        for line in lines:
            if len(line) == 0:
                continue

            raw_fields = line.split("|")

            fields = dict(zip(field_keys, raw_fields[1:len(field_keys)]))

            # how many blocks of var_keys after initial fields
            var_offset = len(field_keys) + 1
            variables  = []
            var_blocks = (len(raw_fields) - var_offset) / len(var_keys)     # how many variables
            vars_only  = raw_fields[var_offset:]

            for offset in xrange(var_blocks):
                variables.append(dict(zip(var_keys, vars_only[offset*len(var_keys):(offset+1)*len(var_keys)])))

            line_val = {'variables':variables}
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





