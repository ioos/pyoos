from pyoos.utils.etree import etree
from owslib.util import nspath, testXMLValue
from paegan.cdm.dsg.features import station
from paegan.cdm.dsg.features.base import point
from paegan.cdm.dsg.collections.station_collection import StationCollection
from shapely.geometry import Point as Location
from datetime import datetime
from dateutil.parser import parse as dtParser

def nsp(tag, namespace):
	return nspath(tag, namespace=namespace)

class USGSParser(object):
	def __init__(self, **kwargs):
		self._wml_ns = 'http://www.cuahsi.org/waterML/1.1/'

	def parse_response(self,response):
		if response is None:
			return None

		xml = etree.fromstring(response)
		time_series = self._read_xml(xml)

		if len(time_series) > 1:
			# retval is a StationCollection
			retval = StationCollection()
			for ts in time_series:
				st = self._timeseries_to_station(ts)
				retval.add_element(st)

		else:
			# retval is a Station
			retval = self._timeseries_to_station(time_series[0])

		return retval

	def _timeseries_to_station(self,time_series):
		retval = station.Station()
		retval.uid = time_series.Code
		retval.name = time_series.Name
		retval.description = str('%s-%s-%s' % (time_series.HUC,time_series.State,time_series.County))

		# collection of variables, sort by datetime
		point_dict = dict()
		for var in time_series.Variables:
			for tv in var.TimeValues:
				if tv[0] not in point_dict:
					point_dict[tv[0]] = point.Point()
					point_dict[tv[0]].time = tv[0]
				point_dict[tv[0]].add_member(dict(name=var.Name,value=tv[1],unit=var.Units))

		for pt in point_dict.values():
			retval.add_element(pt)

		retval.set_location(Location(float(time_series.Location[0]), float(time_series.Location[1])))

		return retval

	def _nsp(self, tag):
		return nsp(tag, self._wml_ns)

	def _read_xml(self, xml):
		"""
			parses xml into list of TimeSeries object
		"""
		series = list()
		for timeSeries in xml.iter(tag=self._nsp('timeSeries')):
			srcinf = timeSeries.find(self._nsp('sourceInfo'))
			scode = testXMLValue(srcinf.find(self._nsp('siteCode')))
			tseries = None
			for s in series:
				if s.Code == scode:
					tseries = s

			if tseries is None:
				tseries = self._read_timeseries_source(timeSeries)
				series.append(tseries)

			# add variable
			var = self._read_variable(timeSeries.find(self._nsp('variable')))
			for tv in self._read_values(timeSeries.find(self._nsp('values'))):
				var.TimeValues = tv
			tseries.Variables = var

		return series

	def _read_timeseries_source(self, timeSeries):
		tsval = dict()

		# go down into sourceInfo
		timeSeries = timeSeries.find(self._nsp('sourceInfo'))

		tsval['code'] = testXMLValue(timeSeries.find(self._nsp('siteCode')))
		tsval['name'] = testXMLValue(timeSeries.find(self._nsp('siteName')))

		tzinfo = timeSeries.find(self._nsp('timeZoneInfo'))
		tzinfo = tzinfo.find(self._nsp('defaultTimeZone'))
		tsval['timezone_offset'] = tzinfo.attrib['zoneOffset']

		loc = timeSeries.find(self._nsp('geoLocation'))
		loc = loc.find(self._nsp('geogLocation'))
		tsval['latitude'] = testXMLValue(loc.find(self._nsp('latitude')))
		tsval['longitude']= testXMLValue(loc.find(self._nsp('longitude')))

		for prop in timeSeries.findall(self._nsp('siteProperty')):
			if prop.attrib['name'] == 'siteTypeCd':
				tsval['type'] = testXMLValue(prop)
			elif prop.attrib['name'] == 'hucCd':
				tsval['huc'] = testXMLValue(prop)
			elif prop.attrib['name'] == 'stateCd':
				tsval['state'] = testXMLValue(prop)
			elif prop.attrib['name'] == 'countyCd':
				tsval['county'] = testXMLValue(prop)

		return TimeSeries(**tsval)

	def _read_variable(self, variable):
		vval = dict()

		vval['code'] = testXMLValue(variable.find(self._nsp('variableCode')))
		vval['name'] = testXMLValue(variable.find(self._nsp('variableName')))
		vval['description'] = testXMLValue(variable.find(self._nsp('variableDescription')))
		vval['type'] = testXMLValue(variable.find(self._nsp('valueType')))
		vval['units'] = testXMLValue(variable.find(self._nsp('unitCode')))
		vval['no_data_value'] = testXMLValue(variable.find(self._nsp('noDataValue')))

		return Variable(**vval)

	def _read_values(self, values):
		tuples = list()
		for value in values.findall(self._nsp('value')):
			val = testXMLValue(value)
			dts = value.attrib['dateTime']
			dt = dtParser(dts)
			tuples.append((dt,val))
		return tuples


class TimeSeries(object):
	"""
		List of properties:
		- site name
		- site code
		- time zone info (?)
		- location (lat/lon)
		- site type
		- huc code
		- state code
		- county code
		- list of variables
	"""
	def __init__(self, **kwargs):
		# kwargs are assumed to be dict items for the time series
		self._name = kwargs.get('name')
		self._code = kwargs.get('code')
		self._tz_offset = kwargs.get('timezone_offset')
		self._type = kwargs.get('type')
		self._huc = kwargs.get('huc')
		self._state = kwargs.get('state')
		self._county = kwargs.get('county')
		self._latitude = kwargs.get('latitude')
		self._longitude = kwargs.get('longitude')
		self._variables = list()

	def get_name(self):
		return self._name

	def set_name(self, name):
		self._name = name

	def get_code(self):
		return self._code

	def set_code(self, code):
		self._code = code

	def get_type(self):
		return self._type

	def set_type(self, stype):
		self._type = stype

	def get_huc(self):
		return self._huc

	def set_huc(self, huc):
		self._huc = huc

	def get_state(self):
		return self._state

	def set_state(self, state):
		self._state = state

	def get_county(self):
		return self._county

	def set_county(self, county):
		self._county = county

	def get_location(self):
		return (self._longitude, self._latitude)

	def set_location(self, longitude, latitude):
		self._longitude = longitude
		self._latitude = latitude

	def get_variables(self):
		return self._variables

	def set_variables(self, variable):
		self._variables.append(variable)

	Name = property(get_name, set_name)
	Code = property(get_code, set_code)
	Type = property(get_type, set_type)
	HUC = property(get_huc, set_huc)
	State = property(get_state, set_state)
	County = property(get_county, set_county)
	Location = property(get_location, set_location)
	Variables = property(get_variables, set_variables)


class Variable(object):
	"""
		List of properties:
		- code
		- name
		- description
		- type
		- units (ft, m, m/s, etc)
		- no data value (generally -999999.0)
		- list of (datetime, value) tuples
		- list of qualifier codes
	"""
	def __init__(self, **kwargs):
		self._code = kwargs.get("code")
		self._name = kwargs.get("name")
		self._type = kwargs.get("type")
		self._description = kwargs.get("description")
		self._units = kwargs.get("units")
		self._miss_val = kwargs.get("no_data_value")
		self._val_tuples = list()
		self._qual_codes = list()

	def get_code(self):
		return self._code

	def set_code(self, code):
		self._code = code

	def get_name(self):
		return self._name

	def set_name(self, name):
		self._name = name

	def get_type(self):
		return self._type

	def set_type(self, stype):
		self._type = stype

	def get_description(self):
		return description

	def set_description(self, desc):
		self._description = desc

	def get_units(self):
		return self._units

	def set_units(self, units):
		self._units = units

	def get_miss_val(self):
		return self._miss_val

	def set_miss_val(self, val):
		self._miss_val = val

	def get_time_values(self):
		return self._val_tuples

	def set_time_values(self, tv):
		self._val_tuples.append(tv)

	def add_time_value(self, dt, value):
		self._val_tuples.append((dt,value))

	def get_qualifier_codes(self):
		return self._qual_codes

	def set_qualifier_codes(self, code):
		self._qual_codes.append(code)

	Code = property(get_code, set_code)
	Name = property(get_name, set_name)
	Type = property(get_type, set_type)
	Description = property(get_description, set_description)
	Units = property(get_units, set_units)
	MissVal = property(get_miss_val, set_miss_val)
	QualifierCodes = property(get_qualifier_codes, set_qualifier_codes)
	TimeValues = property(get_time_values, set_time_values)

