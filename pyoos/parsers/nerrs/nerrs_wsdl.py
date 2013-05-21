from pyoos.utils.etree import etree
from owslib.util import nspath, testXMLValue
from datetime import datetime
from paegan.cdm.dsg.features.station import Station
from paegan.cdm.dsg.features.base.point import Point
from paegan.cdm.dsg.collections.station_collection import StationCollection
from shapely.geometry import Point as Location


def nsp(element_tag, namespace):
	return nspath(element_tag, namespace=namespace)

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

def month(m):
	return {
		'Jan':1,
		'Feb':2,
		'Mar':3,
		'Apr':4,
		'May':5,
		'Jun':6,
		'Jul':7,
		'July':7,
		'Aug':8,
		'Sep':9,
		'Oct':10,
		'Nov':11,
		'Dec':12
	}[m]

def check_for_tag(t):
	try:
		[
			'data',
			'Station_Code',
			'DateTimeStamp',
			'utcStamp',
			'ID',
			'Historical'
		].index(t)
		return False
	except:
		pass
	return True

class WsdlReply(object):

	def __init__(self, wsdl_response):
		self._root = wsdl_response
		self._NS1 = 'http://webservices2'

	def parse_station_collection(self, cb_func, cb_args, desired_stations):
		"""
			Function to group Stations into a StationCollection
			- cb_func: the get_station function to call from the nerr collector
			- cb_args: arguments to pass along into the get_station function
			- desired_stations: list of stations that are to be added into the collections
			returns a StationCollection object
		"""
		if not isinstance(cb_args, dict):
			return None

		if not isinstance(desired_stations, list) or len(desired_stations) < 1:
			return None

		retval = StationCollection()

		for ds in desired_stations:
			elem = cb_func(ds.code, site_id=ds.id, metadata=ds, **cb_args)
			retval.add_element(elem)

		return retval

	def parse_station(self, metadata, data):
		"""
			Creates a Station object from metadata and data for the station
			- metadata: NerrStation object
			- data: list of NerrData objects
			returns a Station object
		"""
		if not isinstance(metadata, NerrStation) or not isinstance(data, list) or len(data) < 1:
			return None

		retval = Station()
		retval.uid = metadata.code
		retval.name = metadata.name
		retval.description = str('%s-%s' % (metadata.id,metadata.code))
		point_dict = dict()
		for d in data:
			for value_date in d.value_and_utc():
				if value_date[0] is not None:
					param = d.get_top_param()
					if value_date[1] not in point_dict:
						point_dict[value_date[1]] = Point()
						point_dict[value_date[1]].time = value_date[1]
					if param.upper() == 'DEPTH':
						point_dict[value_date[1]].location = Location(metadata.location.longitude, metadata.location.latitude, float(value_date[0]))
					else:
						point_dict[value_date[1]].add_member(dict(name=param,value=value_date[0],unit=unit(param)))

		for point in point_dict.values():
			retval.add_element(point)

		retval.set_location(Location(metadata.location.longitude, metadata.location.latitude))

		return retval

	def parse_metadata(self, nerrFilter=False, **kwargs):
		retval = list()
		try:
			st_code = kwargs.get('station_code')
			for data in self._root.findall('data'):
				if st_code is not None:
					if st_code == testXMLValue(data.find('Station_Code')):
						retval.append(NerrStation(data))
				else:
					retval.append(NerrStation(data))
		except:
			retval = None
			raise

		if retval is not None and len(retval) < 1:
			retval = None

		if retval is None and nerrFilter == True:
			raise ValueError(str('No stations associated with given site_id'))
		elif retval is None and kwargs.get('station_code') is not None:
			raise ValueError(str('Unable to find station with code: %s' % (kwargs.get('station_code'))))

		return retval

	def parse_data(self, **kwargs):
		retval = None
		try:
			retval = self.__get_data()
		except:
			retval = None
			pass
		return retval


	def __get_data(self):
		retval = NerrDataCollection()
		for data in self._root.findall('data'):
			retval.add_data(NerrData(data))
		return retval


class NerrDataCollection(object):
	def __init__(self):
		self._data = list()
		return

	# overload
	def __len__(self):
		return len(self._data)

	def __params(self):
		retval = list()
		for data in self._data:
			for p in data.list_params():
				try:
					retval.index(p)
				except ValueError:
					retval.append(p)
					pass
				except:
					raise

		return retval

	def get_top_param(self):
		return self.__params()[0]

	def add_data(self, data):
		self._data.append(data)

	def get_values(self, param=None, date_time=None):
		if param is None:
			param = self.get_top_param()

		if date_time is None:
			retval = list()
			for data in self._data:
				retval.append(data.get_value(param))
			return retval

		if date_time is not None:
			retval = list()
			for data in self._data:
				if data.valid_datetime(date_time):
					retval.append(data.get_value(param))
			return retval

		return None

	def value_and_utc(self, param=None):
		retval = list()

		if param is None:
			param = self.get_top_param()

		for data in self._data:
			retval.append((data.get_value(param), data.utc._dt[0]))

		return retval


class NerrData(object):
	def __init__(self, data_root):
		self._root = data_root

		if self._root.find('ID') is not None:
			self.id = testXMLValue(self._root.find('ID'))
		if self._root.find('Station_Code') is not None:
			self.code = testXMLValue(self._root.find('Station_Code'))
		# set params as attributes
		self._param_list = list()
		for child in self._root.iter():
			if check_for_tag(child.tag):
				if child.text is not None:
					setattr(self, child.tag, float(testXMLValue(child)))
				else:
					setattr(self, child.tag, None)
				self._param_list.append(child.tag)
		# set date object
		self.local = NerrDate(testXMLValue(self._root.find('DateTimeStamp')))
		self.utc = NerrDate(testXMLValue(self._root.find('utcStamp')))

	def get_value(self, param):
		return getattr(self, param, None)

	def list_params(self):
		return self._param_list

	def get_all_values(self):
		retval = dict()
		for param in self._param_list:
			retval[param] = getattr(self, param, None)
		return retval

	def valid_datetime(self, dt_str):
		dt_split = dt_str.split()
		dt = None
		if len(dt_split) > 1:
			dt = datetime.strptime(dt_str,'%m/%d/%Y %H:%M')
		else:
			dt = datetime.strptime(dt_str,'%m/%d/%Y')

		if dt is None:
			return False

		local_dt = self.local._dt[0]

		if len(dt_split) == 1:
			# compare dates
			if dt.date() < local_dt.date() or dt.date() > local_dt.date():
				return False
		else:
			# compare date times
			if dt < local_dt or dt > local_dt:
				return False
		return True

class NerrDate(object):
	def __init__(self, dt_str=None):
		self._dt = list()
		if dt_str is not None:
			self.set_datetime(dt_str)

	def __get__(self, obj, objtype):
		return self.get_datetime_string()

	def __set__(self, obj, value):
		self.set_datetime(value)

	def __get_datetime(self, dt_str):
		if isinstance(dt_str, str) or isinstance(dt_str, unicode):
			ret = list()
			try:
				ret.append(datetime.strptime(dt_str, '%m/%d/%Y %H:%M'))
			except:
				periods = dt_str.split(';')
				for p in periods:
					p_spl = p.split('-')
					for dt in p_spl:
						dt_spl = dt.split()
						if len(dt_spl) == 2:
							mth = month(dt_spl[0])
							yr = int(dt_spl[1])
							ret.append(datetime(yr,mth,1))
						elif len(dt_spl) == 1:
							yr = int(dt_spl[0])
							ret.append(datetime(yr,1,1))
						else:
							# add today as date
							today = datetime.strptime(datetime.today().date().strftime('%m/%d/%Y'),'%m/%d/%Y')
							if today not in ret:
								ret.append(today)
			return ret

		return None

	def get_datetime_string(self, **kwargs):
		ret = list()
		for dt in self._dt:
			if kwargs.get('date') is not None:
				ret.append(dt.date().strftime('%m/%d/%Y'))
			elif kwargs.get('time') is not None:
				ret.append(dt.time().strftime('%H:%M'))
			else:
				ret.append(dt.strftime('%m/%d/%Y %H:%M'))
		return ret

	def set_datetime(self, dt, index=-1):
		if isinstance(dt, datetime):
			if index < 0:
				self._dt.append(dt)
			else:
				self._dt[index] = dt
		elif isinstance(dt,str) or isinstance(st,unicode):
			dt_list = self.__get_datetime(dt)
			if len(dt_list) == 1 and index >= 0:
				self._dt[index] = dt_list[0]
			else:
				for dt_obj in dt_list:
					self._dt.append(dt_obj)

		self._dt.sort()

	def get_start(self, **kwargs):
		ret = self.get_datetime_string(**kwargs)
		return ret[0]

	def get_end(self, **kwargs):
		ret = self.get_datetime_string(**kwargs)
		return ret[len(ret)-1]


class NerrStation(object):
	def __init__(self, data_root):
		self._root = data_root
		# parse info
		#naming
		self.id = testXMLValue(self._root.find("NERR_Site_ID"))
		self.code = testXMLValue(self._root.find("Station_Code"))
		self.name = testXMLValue(self._root.find("Station_Name"))
		#location
		self.location = NerrLocation(self._root)
		# statuse/dates
		self.status = testXMLValue(self._root.find("Status"))
		self.activity = NerrDate(testXMLValue(self._root.find("Active_Dates")))
		# parameters
		params = testXMLValue(self._root.find("Params_Reported"))
		if params is not None:
			self.parameters = params.split(',')
		else:
			self.parameters = None
		# other
		self.reserve_name = testXMLValue(self._root.find("Reserve_Name"))


class NerrLocation(object):
	def __init__(self, root):
		self.latitude = float(testXMLValue(root.find("Latitude")))
		self.longitude = float(testXMLValue(root.find("Longitude")))
		self.state = testXMLValue(root.find("State"))
		if len(self.state) < 3:	# upper case if state initials
			self.state = self.state.upper()
