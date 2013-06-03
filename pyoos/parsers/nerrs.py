# -*- coding: utf-8 -*-

from pyoos.utils.etree import etree
from owslib.util import testXMLValue
from datetime import datetime
from paegan.cdm.dsg.features.station import Station
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.collections.station_collection import StationCollection
from shapely.geometry import Point as sPoint

import pytz
from pyoos.utils.asatime import AsaTime
from paegan.cdm.dsg.member import Member

def units(param):
    # http://cdmo.baruch.sc.edu/documents/manual.pdf
    units = {
        # Water Quality
        'Temp'      :       '°C',
        'SpCond'    :       'mS/cm',
        'Sal'       :       'ppt',
        'DO_pct'    :       '%',
        'DO_mgl'    :       'mg/L',
        'cDepth'    :       'm',
        'Level'     :       'm',
        'cLevel'    :       'm',
        'pH'        :       '',
        'Turb'      :       'NTU',
        'ChlFluor'  :       'ug/L',
        # Meterological
        'ATemp'     :       '°C',
        'RH'        :       '%',
        'BP'        :       'mb',
        'WSpd'      :       'm/s',
        'MaxWSpd'   :       'm/s',
        'MaxWSpdT'  :       'hh:mm',
        'Wdir'      :       '°TN',
        'SDWDir'    :       'sd',
        'TotPAR'    :       'mmoles/m^2',
        'TotPrcp'   :       'mm',
        'CumPrcp'   :       'mm',
        'TotSoRad'  :       'watts/m^2',
        # Nutrient and Pigment
        'PO4F'      :       'mg/L',
        'NH4F'      :       'mg/L',
        'NO2F'      :       'mg/L',
        'NO3F'      :       'mg/L',
        'NO23F'     :       'mg/L',
        'CHLA_N'    :       'µg/L'
    }
    return units.get(param)

def standard(param):
    # http://cdmo.baruch.sc.edu/documents/manual.pdf
    standards = {
        # Water Quality
        'Temp'      :       'sea_water_temperature',
        'SpCond'    :       'specific_conductance',
        'Sal'       :       'sea_water_salinity',
        'DO_pct'    :       'oxygen_concentration_in_sea_water',
        'DO_mgl'    :       'oxygen_concentration_in_sea_water',
        'cDepth'    :       'depth',
        'Level'     :       'depth',
        'cLevel'    :       'depth',
        'pH'        :       'sea_water_acidity',
        'Turb'      :       'sea_water_turbidity',
        'ChlFluor'  :       'chlorophyll_fluorescence_in_sea_water',
        # Meterological
        'ATemp'     :       'air_temperature',
        'RH'        :       'relative_humidity',
        'BP'        :       'air_pressure',
        'WSpd'      :       'wind_sped',
        'MaxWSpd'   :       'wind_speed_of_gust',
        'MaxWSpdT'  :       'time_of_max_wind_speed',
        'Wdir'      :       'wind_direction_from_true_north',
        'SDWDir'    :       'wind_direction_standard_deviation',
        'TotPAR'    :       'total_par_LiCor',
        'TotPrcp'   :       'total_precipitation',
        'CumPrcp'   :       'cumulative_precipitation',
        'TotSoRad'  :       'total_solar_radiation',
        # Nutrient and Pigment
        'PO4F'      :       'orthophosphate_concentration_in_sea_water',
        'NH4F'      :       'ammomium_concentration_in_sea_water',
        'NO2F'      :       'nitrite_concentration_in_sea_water',
        'NO3F'      :       'nitrate_concentration_in_sea_water',
        'NO23F'     :       'nirire_and_nirtrate_concentration_in_sea_water',
        'CHLA_N'    :       'chlorophyll_concentration_in_sea_water'
    }
    return standards.get(param)

class NerrsToPaegan(object):

    def __init__(self, response_list, nerrs_stations=None):
        assert isinstance(response_list, dict)

        if nerrs_stations is None:
            from pyoos.collectors.nerrs.nerrs_soap import NerrsSoap
            nerrs_stations = NerrsSoap().stations

        def get_station(feature):
            for s in nerrs_stations:
                if s['Station_Code'].lower() == feature.lower():
                    return s

        skip_tags = ["DateTimeStamp","utcStamp","data","MaxWSpdT"]

        stations = []
        for feature,response in response_list.iteritems():
            if not isinstance(response, etree._Element):
                response = etree.fromstring(response)

            feature = get_station(feature)

            s = Station()
            s.uid = feature['Station_Code']
            s.name = feature['Station_Name']
            s.location = sPoint(float(feature['Longitude']), float(feature['Latitude']), 0)
            s.set_property("state", feature['State'])
            s.set_property("siteid", feature['NERR_Site_ID'])
            s.set_property("horizontal_crs", "EPSG:4326")
            s.set_property("vertical_units", "m")
            s.set_property("vertical_crs", "EPSG:4297")
            s.set_property("location_description", feature['Reserve_Name'])

            for data in response.findall(".//data"):
                p = Point()
                t = AsaTime.parse(testXMLValue(data.find("utcStamp")))
                t = t.replace(tzinfo=pytz.utc)
                p.time = t
                p.location = s.location
                for child in data:
                    if child.tag not in skip_tags:
                        try:
                            val = float(child.text)
                            p.add_member(Member(value=val, unit=units(child.tag), name=child.tag, description=child.tag, standard=standard(child.tag)))
                        except TypeError:
                            # Value was None
                            pass
                            

                s.add_element(p)  

            stations.append(s)            

        self.feature = StationCollection(elements=stations)