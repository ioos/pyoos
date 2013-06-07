import pytz
from owslib.etree import etree

from shapely.geometry import Point as sPoint
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.features.station import Station as Station
from paegan.cdm.dsg.collections.station_collection import StationCollection
from paegan.cdm.dsg.member import Member
#from dateutil import parser
from datetime import datetime

class AwcToPaegan(object):
    def __init__(self, awc_data):
        
        if isinstance(awc_data, str) or isinstance(awc_data, unicode):
            try:
                self._root = etree.fromstring(str(awc_data))
            except ValueError:
                # Strip out the XML header due to UTF8 encoding declaration
                self._root = etree.fromstring(awc_data[56:])
        else:
            raise ValueError("Cannot parse response into ElementTree xml object")

        #response = WaterML_1_1(self._root).response
        '''Code to get station iterator goes here
        '''
        stations = []
        station_lookup = []
        
        s = Station()
        for metar in self._root.iter('METAR'):
            s = Station()
            s.uid = metar.find("station_id").text
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

            times = {}
            variables = ["elevation_m", "raw_text", "temp_c", "dewpoint_c", "wind_dir_degrees", "wind_speed_kt", "visibility_statute_mi", "altim_in_hg", "wx_string", "sky_condition", "flight_category", "flight_category"]
            for variable in variables:
                for time_string in metar.find("observation_time").text.split(","):
                        dt = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%SZ")
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=pytz.utc)
                        dt = dt.astimezone(pytz.utc)
                        
                        if dt not in times.keys():
                            times[dt] = []
                        try:
                            if variable in set(["raw_text", "flight_catagory", "wx_string"]):
                                times[dt].append(Member(value=metar.find(variable).text, unit=None, name=variable, description=variable, standard=None))
                            elif variable == "sky_condition":
                                sky_condition = []
                                for cond in metar.findall(variable):
                                    cover = cond.attrib["sky_cover"]
                                    try:
                                        alt = cond.attrib["cloud_base_ft_agl"]
                                    except:
                                        alt = None
                                    sky_condition.append({sky_cover:cover, cloud_base_ft_agl:alt})
                                times[dt].append(Member(value=sky_condition, unit="ft_above_ground_level", name=variable, description=variable, standard=None))
                            else:
                                times[dt].append(Member(value=float(metar.find(variable).text), unit=variable.split("_")[-1], name=variable, description=variable, standard=None))
                        except:
                            pass
                            
            #station = stations[station_lookup.index(station_code)]
            for dts,members in times.iteritems():
                p = Point()
                p.time = dts
                p.location = s.location
                p.members = members
                s.add_element(p)
        
        self.feature = StationCollection(elements=stations)
        
