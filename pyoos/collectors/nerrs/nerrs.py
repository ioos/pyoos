from pyoos.collectors.collector import Collector
from suds.client import Client
from urllib2 import urlopen, Request, HTTPError
from pyoos.parsers.soap.nerrs_wsdl import WsdlReply as Reply
from pyoos.cdm.features.station import Station
from pyoos.cdm.features.point import Point
from shapely.geometry import Point as Location

DEBUG = True
WSDL_HTTP = "http://cdmo.baruch.sc.edu/webservices2/requests.cfc?wsdl"

class NerrsWSDL(Collector):
	def __init__(self, **kwargs):
		super(NerrsWSDL,self).__init__()
		self.client = Client(url=WSDL_HTTP)

	def get_station(self, station_code, **kwargs):
		"""
			retrieves the metadata and data for a station and returns a populated cdm Station object
		"""
		metadata = self.get_metadata(station_code=station_code, site_id=kwargs.get('site_id'), test=kwargs.get('test'))
		metadata = metadata[0]
		# need to explore the limitations requested by the user in order to define what we are retrieving from nerrs
		min_date = kwargs.get('min_date')
		if min_date is None:
			min_date = metadata.activity.get_start_date()

		max_date = kwargs.get('max_date')
		if max_date is None:
			max_date = metadata.activity.get_latest_date()

		data = list()
		param = kwargs.get('observed_property')
		if param is None:
			for p in metadata.parameters:
				# get data for each param
				data.append(self.get_station_data(station_code=station_code, min_date=min_date, max_date=max_date, param=p, test=kwargs.get('test')))
		else:
			data.append(self.get_station_data(station_code=station_code, min_date=min_date, max_date=max_date, param=param, test=kwargs.get('test')))

		retval = Station()
		# set metadata
		retval.set_uid(station_code)
		retval.set_name(metadata.name)
		retval.set_description(str('%s-%s' % (metadata.id, metadata.code)))
		# add points
		pt_dict = dict()
		for d in data:
			if param is None:
				for p in metadata.parameters:
					for dv in d.get_value_and_utc_datetime(p):
						if dv[0] is not None:
							if not pt_dict.has_key(dv[1]):
								pt_dict[dv[1]] = Point()
								pt_dict[dv[1]].set_time(dv[1])
							if p.upper() == 'DEPTH':
								# set location with depth value
								pt_dict[dv[1]].location = Location(metadata.location.longitude, metadata.location.latitude, float(dv[0]))
							else:
								pt_dict[dv[1]].add_member(dict(name=p,value=dv[0],unit=unit(p)))
			else:
				for dv in d.get_value_and_utc_datetime(param):
					if dv[0] is not None:
						if not pt_dict.has_key(dv[1]):
							pt_dict[dv[1]] = Point()
							pt_dict[dv[1]].set_time(dv[1])
						pt_dict[dv[1]].add_member(dict(name=p,value=dv[0],unit=unit(p)))

		for pt in pt_dict.values():
			retval.add_element(pt)

		# set location, this will set locations for any points that have yet to have a location set
		retval.set_location(Location(metadata.location.longitude, metadata.location.latitude))

		return retval

	def get_metadata(self, **kwargs):
		global DEBUG, WSDL_HTTP
		# use suds to generate the soap request (though it will fail)
		if kwargs.get("test") is None:
			if kwargs.get("site_id") is not None:
				#use NerrFilter request
				try:
					self.client.service.NERRFilterStationCodesXMLNew(kwargs.get("site_id"))
				except:
					pass
				data = str(self.client.last_sent())
				soap_header = dict(soapaction='NERRFilterStationCodesXMLNew')
			else:
				try:
					self.client.service.exportStationCodesXMLNew()
				except Exception, e:
					pass
				data = str(self.client.last_sent())
				soap_header = dict(soapaction='exportStationCodesXMLNew')

			self.request = Request(url=WSDL_HTTP, data=data, headers=soap_header)

			try:
				self.response = urlopen(self.request)
			except HTTPError:
				if e.getcode() == 500 and kwargs.get('site_id') is not None:
					raise ValueError(str('Unknown site_id: %s' % (kwargs.get('site_id'))))
				else:
					raise
				return None
			except:
				raise
				return None

			self.xml_response = self.response.read()

			# save to temp file for testing
			if DEBUG == True:
				if kwargs.get("site_id") is None:
					f = open('./tmp/tempfile.txt', 'w')
					f.write(self.xml_response)
					f.close()
				else:
					f = open(str('./tmp/%s_tempfile.txt' % (kwargs.get('site_id'))), 'w')
					f.write(self.xml_response)
					f.close()

			self.response.close()
			reply = Reply(self.xml_response)
			return reply.parse_station_response(station_code=kwargs.get("station_code"))
		else:
			if kwargs.get('site_id') is None:
				f = open('./tmp/tempfile.txt', 'r')
				self.xml_response = f.read()
				f.close()
			else:
				f = open(str('./tmp/%s_tempfile.txt' % (kwargs.get('site_id'))), 'r')
				self.xml_response = f.read()
				f.close()

			reply = Reply(self.xml_response)
			return reply.parse_station_response(station_code=kwargs.get("station_code"))

	def get_station_data(self, **kwargs):
		if kwargs.get('min_date') is not None and kwargs.get('max_date') is not None:
			return self.__get_all_params_bound(kwargs.get('station_code'), kwargs.get('min_date'), kwargs.get('max_date'), kwargs.get('param'), kwargs.get('test'))
		elif kwargs.get('station_code') is not None and kwargs.get('param') is not None:
			return self.__get_single_param(kwargs.get('station_code'), kwargs.get('param'), kwargs.get('recs'), kwargs.get('test'))
		elif kwargs.get('station_code') is not None:
			return self.__get_all_params(kwargs.get('station_code'), kwargs.get('recs'), kwargs.get('test'))

		return None

	def __get_all_params_bound(self,station_code,min_date,max_date,param,test=None):
		global DEBUG, WSDL_HTTP

		if test is None:
			test = False

		f_mid = min_date.replace('/','-')
		f_mad = max_date.replace('/','-')

		if test == True:
			f = open(str('./tmp/%s_%s_%s_data.txt' % (station_code,f_mid,f_mad)), 'r')
			self.data_xml = f.read()
			f.close()
		else:
			try:
				self.client.service.exportAllParamsDateRangeXMLNew(station_code,min_date,max_date,param)
			except:
				pass
			data = str(self.client.last_sent())
			soap_header = dict(soapaction='exportAllParamsDateRangeXMLNew')
			self.request = Request(url=WSDL_HTTP, data=data, headers=soap_header)

			try:
				self.response = urlopen(self.request)
			except HTTPError, e:
				if e.getcode() == 500:
					raise ValueError(str('Invalid station_code: %s or date range: %s-%s or param: %s' % (station_code,min_date,max_date,param)))
				else:
					raise
				return None
			except:
				raise
				return None

			self.data_xml = self.response.read()

		if DEBUG == True:
			f = open(str('./tmp/%s_%s_%s_data.txt' % (station_code,f_mid,f_mad)), 'w')
			f.write(self.data_xml)
			f.close()

		reply = Reply(self.data_xml)
		return reply.parse_data_date_range()
		
	def __get_single_param(self,station_code,param,recs=None,test=None):
		global DEBUG, WSDL_HTTP

		if recs is None:
			recs = '100'
		if test is None:
			test = False;

		if test == True:
			f = open(str('./tmp/%s_%s_data.txt' % (station_code,param)), 'r')
			self.data_xml = f.read()
			f.close()
		else:
			try:
				self.client.service.exportSingleParamXMLNew(station_code,recs,param)
			except:
				pass
			data = str(self.client.last_sent())
			soap_header = dict(soapaction='exportSingleParamXMLNew')
			self.request = Request(url=WSDL_HTTP, data=data, headers=soap_header)

			try:
				self.response = urlopen(self.request)
			except HTTPError, e:
				if e.getcode() == 500:
					raise ValueError(str('Invalid station_code: %s or param: %s' % (station_code,param)))
				else:
					raise
				return None
			except:
				raise
				return None

			self.data_xml = self.response.read()

		if DEBUG == True:
			f = open(str('./tmp/%s_%s_data.txt' % (station_code,param)), 'w')
			f.write(self.data_xml)
			f.close()

		reply = Reply(self.data_xml)
		return reply.parse_data_single_param()

	def __get_all_params(self,station_code,recs=None,test=None):
		global DEBUG, WSDL_HTTP

		if recs is None:
			recs = '100'
		if test is None:
			test = False

		if test == True:
			f = open(str('./tmp/%s_data.txt' % (station_code)), 'r')
			self.data_xml = f.read()
			f.close()
		else:
			try:
				self.client.service.exportAllParamsXMLNew(station_code,recs)
			except:
				pass
			data = str(self.client.last_sent())
			soap_header = dict(soapaction='exportAllParamsXMLNew')
			self.request = Request(url=WSDL_HTTP, data=data, headers=soap_header)

			try:
				self.response = urlopen(self.request)
			except HTTPError, e:
				if e.getcode() == 500:
					raise ValueError(str('Invalid station_code: %s' % (station_code)))
				else:
					raise
				return None
			except:
				raise
				return None

			self.data_xml = self.response.read()

		if DEBUG == True:
			f = open(str('./tmp/%s_data.txt' % (station_code)), 'w')
			f.write(self.data_xml)
			f.close()

		reply = Reply(self.data_xml)
		return reply.parse_data_all_params()


def unit(param):
	return {
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
		'ChlFluor':'\\u03bcg/L'.decode('unicode-escape')
	}[param]