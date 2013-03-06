from pyoos.collectors.collector import Collector
from suds.client import Client
from urllib2 import urlopen, Request, HTTPError
from pyoos.parsers.nerrs.nerrs_wsdl import WsdlReply as Reply
from owslib.util import nspath
from pyoos.utils.etree import etree

class NerrsWSDL(Collector):
	def __init__(self, **kwargs):
		super(NerrsWSDL,self).__init__()
		self._WSDL_HTTP = 'http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl'
		self._SOAPENV = 'http://schemas.xmlsoap.org/soap/envelope/'
		self.client = Client(url=self._WSDL_HTTP)

	def get_stations_by_bbox(self, south, west, north, east, **kwargs):
		"""
			retrieves Station objects from Nerrs determined by the boundaries given
			- south: the southern-most latitude (in degrees North)
			- west: western-most longitude (in degrees West)
			- north: northern-most latitude (in degrees North)
			- east: eastern-most longitude (in degrees West)
			optionals:
			- min_date
			- max_date
			- observed_property
			returns a StationCollection object from the parser
		"""
		metadata = self.__get_metadata()
		desired_stations = list()
		for station in metadata:
			if station.location.longitude >= east and station.location.longitude <= west:
				if station.location.latitude <= north and station.location.longitude >= south:
					desired_stations.append(station)
		args = dict(min_date=kwargs.get('min_date'),max_date=kwargs.get('max_date'),observed_property=kwargs.get('observed_property'))
		reply = Reply(None)
		return reply.parse_station_collection(self.get_station, args, desired_stations)

	def get_stations_by_latlon(self, latitudes, longitudes, **kwargs):
		"""
			retrieves Station objects from Nerrs determined by the series of latitudes and longitudes
			- latitudes: comma-deliminated string of latitude values
			- longitudes: comma-deliminated string of longitude values
			optionals:
			- min_date
			- max_date
			- observed_property
			returns a StationCollection object from the parser
		"""
		if latitudes is None or longitudes is None:
			return None

		lats = str(latitudes).split(',')
		lons = str(longitudes).split(',')
		# make sure the lists are equal in size
		while len(lats) > len(lons):
			noop = lats.pop()
		while len(lons) > len(lats):
			noop = lons.pop()

		metadata = self.__get_metadata()
		desired_stations = list()
		for station in metadata:
			for index, value in enumerate(lats):
				if station.location.latitude == float(value) and station.location.longitude == float(lons[index]) and station not in desired_stations:
					desired_stations.append(station)
		args = dict(min_date=kwargs.get('min_date'),max_date=kwargs.get('max_date'),observed_property=kwargs.get('observed_property'))
		reply = Reply(None)
		return reply.parse_station_collection(self.get_station, args, desired_stations)

	def get_station(self, station_code, **kwargs):
		"""
			retrieves a Station object from Nerrs, found by the given station code
			- station_code: the uid of the station
			optionals:
			- metadata
			- min_date
			- max_date
			- observed_property
		"""
		if station_code is None:
			return None

		metadata = kwargs.get('metadata')
		if metadata is None:
			metadata = self.__get_metadata(station_code=station_code, site_id=kwargs.get('site_id'))
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
			d = self.__get_station_data(station_code=station_code, min_date=min_date, max_date=max_date, param=p)
			if d is not None:
				data.append(d)

		reply = Reply(None)
		return reply.parse_station(metadata, data)

	def __get_metadata(self, **kwargs):
		# use suds to generate the soap request (though it will fail)
		if kwargs.get("site_id") is not None:
			#use NerrFilter request
			try:
				self.client.service.NERRFilterStationCodesXMLNew(kwargs.get("site_id"))
			except:
				pass
			soap_header = dict(soapaction='NERRFilterStationCodesXMLNew')
			nerrFilter = True
		else:
			try:
				self.client.service.exportStationCodesXMLNew()
			except:
				pass
			soap_header = dict(soapaction='exportStationCodesXMLNew')
			nerrFilter = False
		
		data = str(self.client.last_sent())
		reply = self.__get_reply_from_response(data, soap_header)

		if reply is None:
			return reply

		return reply.parse_metadata(nerrFilter=nerrFilter, station_code=kwargs.get("station_code"))

	def __get_station_data(self, **kwargs):
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

		return reply.parse_data()
		
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

		return reply.parse_data()

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

		return reply.parse_data()

	def __get_reply_from_response(self, data, soap_header, xml=False):
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
		xml_root = xml_root.find(".//returnData")

		if xml is True:
			return xml_root

		return Reply(xml_root)
