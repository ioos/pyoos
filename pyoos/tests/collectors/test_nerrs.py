
import unittest
from datetime import date
from pytest import raises
from pyoos.collectors.nerrs.nerrs import NerrsWSDL
from shapely.geometry import Point

class NerrTest(unittest.TestCase):

	def setUp(self):
		self.nerrs = NerrsWSDL()

	def test_get_metadata(self):
		"""
			<?xml version="1.0" encoding="UTF-8"?>
			<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
			xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> 
				<soapenv:Body>
					<ns1:exportStationCodesXMLNewResponse soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:ns1="http://webservices2"> 
						<exportStationCodesXMLNewReturn xsi:type="ns2:Document" xmlns:ns2="http://xml.apache.org/xml-soap">
							<returnData>
          						<data count="1">
					                <NERR_Site_ID>ace</NERR_Site_ID>
					                <Station_Code>acebbnut</Station_Code>
					                <Station_Name>Big Bay</Station_Name>
					                <Lat_Long>32&#xB0; 29' 38.76 N, 80&#xB0; 19' 26.76 W</Lat_Long>
					                <Latitude>32.4941</Latitude>
					                <Longitude>80.3241</Longitude>
					                <Status>Active</Status>
					                <Active_Dates>Feb 2002-</Active_Dates>
					                <State>sc</State>
					                <Reserve_Name>Ashepoo Combahee Edisto Basin</Reserve_Name>
					                <Params_Reported>NO23F,PO4F,CHLA_N,NO3F,NO2F,NH4F</Params_Reported>
					                <Real_Time/>
       							</data>
       							....
      						</returnData>
      					</exportStationCodesXMLNewReturn>
      				</ns1:exportStationCodesXMLNewResponse>
      			</soapenv:Body>
      		</soapenv:Envelope>
		"""

		stations = self.nerrs.get_metadata()

		assert len(stations) == 318

		# check that each station parsed properly
		for st in stations:
			assert st.id is not None
			assert st.code is not None
			assert st.name is not None
			assert st.location.latitude is not None
			assert st.location.longitude is not None
			assert st.location.state is not None
			assert st.status is not None
			assert st.activity is not None
			if st.parameters is not None:
				assert len(st.parameters) > 0
			assert st.reserve_name is not None

		# check for the example node above
		for st in stations:
			if st.id == 'ace' and st.code == 'acebbnut':
				assert st.name == "Big Bay"
				assert st.location.latitude == 32.4941
				assert st.location.longitude == 80.3241
				assert st.location.state == 'SC'
				assert st.status == 'Active'
				# check active dates
				assert st.activity.get_start_date() == '02/01/2002'
				today = date.today().strftime("%m/%d/%Y")
				assert st.activity.get_latest_date() == today
				# check params
				assert st.parameters.index('NO23F') >= 0
				assert st.parameters.index('PO4F') >= 0
				assert st.parameters.index('CHLA_N') >= 0
				assert st.parameters.index('NO3F') >= 0
				assert st.parameters.index('NO2F') >= 0
				assert st.parameters.index('NH4F') >= 0

	def test_get_specific_station(self):
		"""
			gets the station that matches both the site_id and station_code (below)
		<data count="23">
            <NERR_Site_ID>apa</NERR_Site_ID>
            <Station_Code>apapcnut</Station_Code>
            <Station_Name>Pilots Cove</Station_Name>
            <Lat_Long>29&#xB0; 36' 28.44 N, 85&#xB0; 1' 10.56 W</Lat_Long>
            <Latitude>29.6079</Latitude>
            <Longitude>85.0196</Longitude>
            <Status>Active</Status>
            <Active_Dates>Apr 2002-</Active_Dates>
            <State>fl</State>
            <Reserve_Name>Apalachicola Bay</Reserve_Name>
            <Params_Reported>PO4F,NH4F,NO2F,NO3F,NO23F,CHLA_N</Params_Reported>
            <Real_Time/>
       </data>

		"""
		station = self.nerrs.get_metadata(site_id='apa', station_code='apapcnut')

		assert station is not None
		assert len(station) == 1

		station = station[0]

		assert station.id == 'apa'
		assert station.code == 'apapcnut'
		assert station.name == 'Pilots Cove'
		assert station.location.latitude == 29.6079
		assert station.location.longitude == 85.0196
		assert station.location.state == 'FL'
		assert station.status == 'Active'
		assert station.activity.get_start_date() == '04/01/2002'
		today = date.today().strftime("%m/%d/%Y")
		assert station.activity.get_latest_date() == today
		assert station.reserve_name == 'Apalachicola Bay'
		assert station.parameters.index('NO23F') >= 0
		assert station.parameters.index('PO4F') >= 0
		assert station.parameters.index('CHLA_N') >= 0
		assert station.parameters.index('NO3F') >= 0
		assert station.parameters.index('NO2F') >= 0
		assert station.parameters.index('NH4F') >= 0

	def test_get_site_stations(self):
		"""
			gets all stations that match the site_id
		"""

		stations = self.nerrs.get_metadata(site_id='kac')

		assert stations is not None
		assert len(stations) == 16

	def test_get_first_station(self):
		"""
			gets the first station matching the code

		<data count="111">
            <NERR_Site_ID>job</NERR_Site_ID>
            <Station_Code>jobjbmet</Station_Code>
            <Station_Name>Jobos Bay Weather</Station_Name>
            <Lat_Long>17&#xB0; 57' 23.71 N, 66&#xB0; 13' 22.69 W</Lat_Long>
            <Latitude>17.956586</Latitude>
            <Longitude>66.222969</Longitude>
            <Status>Active</Status>
            <Active_Dates>Jan 2001-</Active_Dates>
            <State>pr</State>
            <Reserve_Name>Jobos Bay</Reserve_Name>
            <Params_Reported>ATemp,RH,BP,WSpd,MaxWSpd,MaxWSpdT,Wdir,SDWDir,TotPrcp,TotPAR,CumPrcp</Params_Reported>
            <Real_Time>R</Real_Time>
       </data>

		"""

		station = self.nerrs.get_metadata(station_code="jobjbmet")

		assert station is not None
		assert len(station) == 1

		station = station[0]

		assert station.id == 'job'
		assert station.code == 'jobjbmet'
		assert station.location.latitude == 17.956586
		assert station.location.longitude == 66.222969
		assert station.location.state == 'PR'
		assert station.status == 'Active'
		assert station.activity.get_start_date() == "01/01/2001"
		today = date.today().strftime("%m/%d/%Y")
		assert station.activity.get_latest_date() == today
		assert station.reserve_name == 'Jobos Bay'

		assert station.parameters.index('ATemp') >= 0
		assert station.parameters.index('RH') >= 0
		assert station.parameters.index('BP') >= 0
		assert station.parameters.index('WSpd') >= 0
		assert station.parameters.index('MaxWSpd') >= 0
		assert station.parameters.index('Wdir') >= 0
		assert station.parameters.index('SDWDir') >= 0
		assert station.parameters.index('TotPrcp') >= 0
		assert station.parameters.index('TotPAR') >= 0
		assert station.parameters.index('CumPrcp') >= 0
		assert station.parameters.index('MaxWSpdT') >= 0

	def test_get_station_data(self):
		"""
			test getting all params from a single station
		"""

		data = self.nerrs.get_station_data(station_code='apapcnut',recs='10')

		assert data is not None
		assert len(data) == 10

		vals = data.get_values(param='PO4F', date_time='09/07/2011')
		assert len(vals) == 1
		assert vals[0] == 0.0030

		vals = data.get_values(param='CHLA_N', date_time='08/03/2011')
		assert len(vals) == 1
		assert vals[0] == 8.3

		nh4f = data.get_values(param='NH4F')

		assert nh4f is not None
		assert len(nh4f) == 10
		assert nh4f[3] == 0.04

		no3f = data.get_values_and_date(param='NO3F')

		assert no3f is not None
		assert len(no3f) == 10
		assert no3f[5] == (None,'02/09/2011 11:27')

	def test_get_single_param(self):
		"""
			get a single param from a station
		"""

		data = self.nerrs.get_station_data(station_code='kacbcwq',param='TEMP',recs='10')

		assert data is not None
		assert len(data) == 10

		vals = data.get_values(date_time='09/24/2003')
		assert len(vals) == 10

		vals = data.get_values(date_time='09/24/2003 13:30')
		assert len(vals) == 1
		assert vals[0] == 10.5

		vals = data.get_values()
		assert len(vals) == 10
		assert vals[3] == 10.3

		vals = data.get_values_and_date()
		assert len(vals) == 10
		assert vals[6] == (10.4, '09/24/2003 14:30')

	def test_single_param_dates(self):
		"""
			get a single param in a date range
		"""

		data = self.nerrs.get_station_data(station_code='kacsdwq',min_date='01/01/2004',max_date='12/01/2004',param='PH')

		assert data is not None
		assert len(data) == 1000

		vals = data.get_values(date_time='11/23/2004')
		assert len(vals) == 96

		vals = data.get_values(date_time='12/01/2004')
		assert len(vals) == 96

	def test_bad_station_code(self):
		"""
			attempt a metadata request with a bad station code
			attempt a metadata request with bad site_id
		"""

		# bad station
		with raises(ValueError):
			data = self.nerrs.get_metadata(station_code='valhalla')
			assert data is None

		# bad site id
		with raises(ValueError):
			data = self.nerrs.get_metadata(site_id='asgard')
			assert data is None

		# bad site id, good station
		with raises(ValueError):
			data = self.nerrs.get_metadata(site_id='asgard', station_code='kacsdwq')
			assert data is None

		# bad station, good site id
		with raises(ValueError):
			data = self.nerrs.get_metadata(site_id='kac', station_code='valhalla')
			assert data is None

	def test_bad_station_data(self):
		"""
			attempt a data request with a bad station code
			attempt data request with bad date ranges
			attempt data request with bad param
		"""

		# bad station
		with raises(ValueError):
			data = self.nerrs.get_station_data(station_code='valhalla')
			assert data is None

		# good station/param, bad dates
		with raises(ValueError):
			data = self.nerrs.get_station_data(station_code='kacsdwq',min_date='01/01/2000',max_date='12/01/2000',param='PH')
			assert data is None

		# good station/dates, bad param
		with raises(ValueError):
			data = self.nerrs.get_station_data(station_code='kacsdwq',min_date='01/01/2004',max_date='12/01/2004',param='HP')
			assert data is None

		# good param/dates, bad station
		with raises(ValueError):
			data = self.nerrs.get_station_data(station_code='valhalla',min_date='01/01/2004',max_date='12/01/2004',param='PH')
			assert data is None

		# good station, bad param
		with raises(ValueError):
			data = self.nerrs.get_station_data(station_code='kacsdwq',param='HP')
			assert data is None

		# good param, bad station
		with raises(ValueError):
			data = self.nerrs.get_station_data(station_code='valhalla',param='PH')
			assert data is None

	def test_get_station_cdm(self):
		"""
			test the station cdm returned from nerrs
		"""

		station = self.nerrs.get_station('acebbwq', site_id='ace', min_date='02/06/2013', max_date='02/10/2013')

		assert station is not None

		station.calculate_bounds()

		for k in station.properties().keys():
			print str('%s - %s', (k, station.get_property(k)))

		assert station.description == 'ace-acebbwq'
		assert station.name == 'Big Bay'
		assert station.uid == 'acebbwq'
		assert station.type == 'timeSeries'
		assert str(station.bbox) == 'POINT (80.3241000000000014 32.4941000000000031)'

		assert station.size == 39

		# print dir(station.get_time_range())
		# print station.get_time_range()
		# print station.elements

		alist = list()
		for m in station.get_unique_members():
			alist.append(m['name'])
		assert alist.index('Temp') >= 0
		assert alist.index('Sal') >= 0
		assert alist.index('DO_pct') >= 0
		assert alist.index('SpCond') >= 0
		assert alist.index('DO_mgl') >= 0
		assert alist.index('pH') >= 0
		assert alist.index('Turb') >= 0

		# depth bounds
		assert station.depth_range[0] == 1.67
		assert station.depth_range[station.size-1] == 3.53

		# time bounds
		assert station.time_range[0].strftime('%m/%d/%Y %H:%M') == '02/06/2013 05:00'
		assert station.time_range[station.size-1].strftime('%m/%d/%Y %H:%M') == '02/06/2013 14:30'