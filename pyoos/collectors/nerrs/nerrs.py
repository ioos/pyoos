from pyoos.collectors.collector import Collector
from suds.client import Client
from urllib2 import urlopen, Request, HTTPError
from pyoos.parsers.soap.nerrs_wsdl import WsdlReply as Reply
from pyoos.cdm.features.station import Station
from pyoos.cdm.features.point import Point
from pyoos.cdm.collections.station_collection import StationCollection
from shapely.geometry import Point as Location
from owslib.util import nspath
from pyoos.utils.etree import etree

def unit(param):
	return {
		# Water Quality
		'Temp':'\\xb0C'.decode('unicode-escape'),
		'SpCond':'mS/cm',
		'Sal':'ppt',
		'DO_pct':'%',
		'DO_mgl':'mg/L',
		'cDepth':'m',
		'Level':'m',
		'cLevel':'m',
		'pH':'',
		'Turb':'NTU',
		'ChlFluor':'\\u03bcg/L'.decode('unicode-escape'),
		# Meterological
		'ATemp':'\\xb0C'.decode('unicode-escape'),
		'RH':'%',
		'BP':'mb',
		'WSpd':'m/s',
		'MaxWSpd':'m/s',
		'MaxWSpdT':'hh:mm',
		'Wdir':'\\xb0'.decode('unicode-escape'),
		'SDWDir':'sd',
		'TotPAR':'mmol/m^2',
		'TotPrcp':'mm',
		'CumPrcp':'mm',
		'TotSoRad':'W/m^2',
		# Nutrient and Pigment
		'PO4F':'mg/L',
		'NH4F':'mg/L',
		'NO2F':'mg/L',
		'NO3F':'mg/L',
		'NO23F':'mg/L',
		'CHLA_N':'\\u03bcg/L'.decode('unicode-escape')
	}[param]

class NerrsWSDL(Collector):
	def __init__(self, **kwargs):
		super(NerrsWSDL,self).__init__()
		self._WSDL_HTTP = 'http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl'
		self._SOAPENV = 'http://schemas.xmlsoap.org/soap/envelope/'
		self.client = Client(url=self._WSDL_HTTP)

	def get_stations_bbox(self, south, west, north, east, **kwargs):
		"""
			lookups stations by bbox (south,west,north,east)
			returns a StationCollection object
		"""
		# will have to get all metadata and just sort through it, filtering it by the bbox
		metadata = self.get_metadata()
		desired_stations = list()
		for nerr in metadata:
			# lat is deg West
			if nerr.location.longitude >= east and nerr.location.longitude <= west:
				# lon is deg North
				if nerr.location.latitude <= north and nerr.location.latitude >= south:
					desired_stations.append(nerr)

		# get Station objects for each of our desired stations
		ret = StationCollection()
		for ds in desired_stations:
			elem = self.get_station(ds.code, site_id=ds.id, min_date=kwargs.get('min_date'), max_date=kwargs.get('max_date'), observed_property=kwargs.get('observed_property'), metadata=ds)
			ret.add_element(elem)

		return ret

	def get_stations_latlon(self, lat, lon, **kwargs):
		"""
			lookups stations by lat/lon points (comma-deliminated)
			returns a StationCollection object
		"""
		# get all metadata, sort through, getting only stations that match our lat/lons
		lats = str(lat).split(',')
		lons = str(lon).split(',')
		if len(lats) != len(lons):
			# reduce the larger list to the size of the other list
			while len(lats) > len(lons):
				noop = lats.pop()
			while len(lons) > len(lats):
				noop = lons.pop()

		metadata = self.get_metadata()
		desired_stations = list()
		for nerr in metadata:
			for i, val in enumerate(lats):
				if nerr.location.latitude == float(val) and nerr.location.longitude == float(lons[i]) and nerr not in desired_stations:
					desired_stations.append(nerr)

		# get a StationCollection of the desired stations
		ret = StationCollection()
		for ds in desired_stations:
			elem = self.get_station(ds.code, site_id=ds.id, min_date=kwargs.get('min_date'), max_date=kwargs.get('max_date'), observed_property=kwargs.get('observed_property'), metadata=ds)
			ret.add_element(elem)

		return ret

	def get_station(self, station_code, **kwargs):
		"""
			retrieves the metadata and data for a station and returns a populated cdm Station object
			returns a Station object
		"""
		metadata = kwargs.get('metadata')
		if metadata is None:
			metadata = self.get_metadata(station_code=station_code, site_id=kwargs.get('site_id'))
			metadata = metadata[0]
		# need to explore the limitations requested by the user in order to define what we are retrieving from nerrs
		min_date = kwargs.get('min_date')
		if min_date is None:
			min_date = metadata.activity.get_start(date=True)

		max_date = kwargs.get('max_date')
		if max_date is None:
			max_date = metadata.activity.get_end(date=True)

		data = list()
		param = kwargs.get('observed_property')
		if param is None:
			param = metadata.parameters
		else:
			param = param.split(',')

		for p in param:
			try:
				d = self.get_station_data(station_code=station_code, min_date=min_date, max_date=max_date, param=p)
				if d is None:
					print str('No data for: %s-%s-%s-%s' % (station_code,min_date,max_date,p))
				else:
					data.append(d)
			except:
				print str('No data for: %s-%s-%s-%s' % (station_code,min_date,max_date,p))

		# data is a list of NerrDataCollection that track 1 param each
		retval = Station()
		# set metadata
		retval.set_uid(station_code)
		retval.set_name(metadata.name)
		retval.set_description(str('%s-%s' % (metadata.id, metadata.code)))
		# add points
		pt_dict = dict()
		for d in data:
			for dv in d.value_and_utc():
				if dv[0] is not None:
					p = d.get_top_param()
					if dv[1] not in pt_dict:
						pt_dict[dv[1]] = Point()
						pt_dict[dv[1]].time = dv[1]
					if p.upper() == 'DEPTH':
						pt_dict[dv[1]].location = Location(metadata.location.longitude, metadata.location.latitude, float(dv[0]))
					else:
						pt_dict[dv[1]].add_member(dict(name=p,value=dv[0],unit=unit(p)))

		for pt in pt_dict.values():
			retval.add_element(pt)

		# set location, this will set locations for any points that have yet to have a location set
		retval.set_location(Location(metadata.location.longitude, metadata.location.latitude))

		return retval

	def get_metadata(self, **kwargs):
		# use suds to generate the soap request (though it will fail)
		if kwargs.get("site_id") is not None:
			#use NerrFilter request
			try:
				self.client.service.NERRFilterStationCodesXMLNew(kwargs.get("site_id"))
			except:
				pass
			soap_header = dict(soapaction='NERRFilterStationCodesXMLNew')
		else:
			try:
				self.client.service.exportStationCodesXMLNew()
			except:
				pass
			soap_header = dict(soapaction='exportStationCodesXMLNew')
		
		data = str(self.client.last_sent())
		reply = self.__get_reply_from_response(data, soap_header)

		if reply is None:
			return reply

		return reply.parse_station_response(station_code=kwargs.get("station_code"))

	def get_station_data(self, **kwargs):
		if kwargs.get('min_date') is not None and kwargs.get('max_date') is not None:
			return self.__get_all_params_bound(kwargs.get('station_code'), kwargs.get('min_date'), kwargs.get('max_date'), kwargs.get('param'))
		elif kwargs.get('station_code') is not None and kwargs.get('param') is not None:
			return self.__get_single_param(kwargs.get('station_code'), kwargs.get('param'), kwargs.get('recs'))
		elif kwargs.get('station_code') is not None:
			return self.__get_all_params(kwargs.get('station_code'), kwargs.get('recs'))

		return None

	def __get_all_params_bound(self,station_code,min_date,max_date,param):
		try:
			self.client.service.exportAllParamsDateRangeXMLNew(station_code,min_date,max_date,param)
		except:
			pass

		data = str(self.client.last_sent())
		soap_header = dict(soapaction='exportAllParamsDateRangeXMLNew')
		
		reply = self.__get_reply_from_response(data, soap_header)

		if reply is None:
			return reply

		return reply.parse_data_date_range()
		
	def __get_single_param(self,station_code,param,recs=None):
		if recs is None:
			recs = '100'

		try:
			self.client.service.exportSingleParamXMLNew(station_code,recs,param)
		except:
			pass

		data = str(self.client.last_sent())
		soap_header = dict(soapaction='exportSingleParamXMLNew')
		
		reply = self.__get_reply_from_response(data, soap_header)

		if reply is None:
			return reply

		return reply.parse_data_single_param()

	def __get_all_params(self,station_code,recs=None):
		if recs is None:
			recs = '100'

		try:
			self.client.service.exportAllParamsXMLNew(station_code,recs)
		except:
			pass

		data = str(self.client.last_sent())
		soap_header = dict(soapaction='exportAllParamsXMLNew')
		
		reply = self.__get_reply_from_response(data, soap_header)

		if reply is None:
			return reply

		return reply.parse_data_all_params()

	def __get_reply_from_response(self, data, soap_header):
		self.request = Request(url=self._WSDL_HTTP, data=data, headers=soap_header)

		try:
			self.response = urlopen(self.request)
		except HTTPError, e:
			if e.getcode() == 500:
				raise ValueError('Invalid value(s) in request, please check input and try again')
			else:
				raise
			return None
		except:
			raise
			return None

		self.response_soap = self.response.read()
		self.response.close()

		# pass in the etree object that points to the return/response point
		xml_root = None
		try:
			xml_root = etree.fromstring(self.response_soap)
		except Exception, e:
			xml_root = etree.fromstring(self.response_soap[38:])

		if hasattr(xml_root, 'getroot'):
			xml_root = xml_root.getroot()

		xml_root = xml_root.find(nspath('Body',namespace=self._SOAPENV))

		return Reply(xml_root)
