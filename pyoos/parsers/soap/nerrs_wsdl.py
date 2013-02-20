from pyoos.utils.etree import etree
from owslib.util import nspath, testXMLValue
from datetime import MINYEAR, datetime

def nsp(element_tag, namespace):
	return nspath(element_tag, namespace=namespace)

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

	def parse_station_response(self, **kwargs):
		retval = list()
		nerrFilter = False
		try:
			resp = nsp('exportStationCodesXMLNewResponse', self._NS1)

			resp = self._root.find(resp)

			if resp is None:
				resp = nsp('NERRFilterStationCodesXMLNewResponse', self._NS1)
				resp = self._root.find(resp)

			ret = 'exportStationCodesXMLNewReturn'
			ret = resp.find(ret)

			if ret is None:
				ret = 'NERRFilterStationCodesXMLNewReturn'
				ret = resp.find(ret)
				nerrFilter = True

			retData = ret.find('returnData')

			st_code = kwargs.get('station_code')
			for data in retData.findall('data'):
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

	def parse_data_single_param(self, **kwargs):
		retval = NerrDataCollection()

		try:
			resp = nsp('exportSingleParamXMLNewResponse', self._NS1)
			ret = 'exportSingleParamXMLNewReturn'

			resp = self._root.find(resp)
			ret = resp.find(ret)
			retData = ret.find('returnData')

			for data in retData.findall('data'):
				retval.add_data(NerrStationData(data))
		except:
			retval = None
			pass

		return retval

	def parse_data_all_params(self, **kwargs):
		retval = NerrDataCollection()

		try:
			resp = nsp('exportAllParamsXMLNewResponse', self._NS1)
			ret = 'exportAllParamsXMLNewReturn'

			resp = self._root.find(resp)
			ret = resp.find(ret)
			retData = ret.find('returnData')

			for data in retData.findall('data'):
				retval.add_data(NerrStationData(data))
		except:
			retval = None
			pass

		return retval

	def parse_data_date_range(self, **kwargs):
		retval = NerrDataCollection()

		try:
			resp = nsp('exportAllParamsDateRangeXMLNewResponse', self._NS1)
			ret = 'exportAllParamsDateRangeXMLNewReturn'

			resp = self._root.find(resp)
			ret = resp.find(ret)
			retData = ret.find('returnData')

			for data in retData.findall('data'):
				retval.add_data(NerrStationData(data))
		except:
			retval = None
			pass

		if retval is not None and len(retval) < 1:
			retval = None
			raise ValueError('No data for given date range')

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

	def add_data(self, data):
		self._data.append(data)

	def get_values(self, param=None, date_time=None):
		if param is None:
			param = self.__params()[0]

		if date_time is None:
			retval = list()
			for data in self._data:
				retval.append(data.get_value(param))
			return retval

		if date_time is not None:
			retval = list()
			for data in self._data:
				if data.is_datetime(date_time):
					retval.append(data.get_value(param))
			return retval

		return None

	def get_values_and_date(self, param=None):
		retval = list()

		if param is None:
			param = self.__params()[0]

		for data in self._data:
			retval.append((data.get_value(param), data.timestamp.get_local_datetime()))

		return retval

	def get_value_and_utc_datetime(self, param=None):
		retval = list()

		if param is None:
			param = self.__params()[0]

		for data in self._data:
			retval.append((data.get_value(param), data.timestamp._utc_dt))

		return retval

class NerrStationData(object):
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
		self.timestamp = NerrDataDate(testXMLValue(self._root.find('DateTimeStamp')), testXMLValue(self._root.find('utcStamp')))

	def get_value(self, param):
		return getattr(self, param, None)

	def list_params(self):
		return self._param_list

	def get_all_values(self):
		retval = dict()
		for param in self._param_list:
			retval[param] = getattr(self, param, None)
		return retval

	def is_datetime(self, dt_str):
		dt_split = dt_str.split()
		dt = None
		if len(dt_split) > 1:
			dt = datetime.strptime(dt_str,'%m/%d/%Y %H:%M')
		else:
			dt = datetime.strptime(dt_str,'%m/%d/%Y')

		if len(dt_split) == 1:
			# compare dates
			if dt.date() < self.timestamp._local_dt.date() or dt.date() > self.timestamp._local_dt.date():
				return False
		else:
			# compare date times
			if dt < self.timestamp._local_dt or dt > self.timestamp._local_dt:
				return False
		return True


class NerrDataDate(object):
	def __init__(self, ldtstr=None, udtstr=None):
		if ldtstr is not None:
			self.set_local_datetime(ldtstr)
		if udtstr is not None:
			self.set_utc_datetime(udtstr)
		return

	def set_local_datetime(self, dt_str):
		self._local_dt = self.__get_datetime(dt_str)

	def set_utc_datetime(self, dt_str):
		self._utc_dt = self.__get_datetime(dt_str)

	def get_local_date(self):
		return self._local_dt.date().strftime('%m/%d/%Y')

	def get_local_time(self):
		return self._local_dt.time().strftime('%H:%M')

	def get_utc_date(self):
		return self._utc_dt.date().strftime('%m/%d/%Y')

	def get_utc_time(self):
		return self._utc_dt.time().strftime('%H:%M')

	def get_local_datetime(self):
		return self._local_dt.strftime('%m/%d/%Y %H:%M')

	def get_utc_datetime(self):
		return self._utc_dt.strftime('%m/%d/%Y %H:%M')

	def __get_datetime(self, dt_str):
		if isinstance(dt_str, str) or isinstance(dt_str, unicode):
			dt = datetime.strptime(dt_str, '%m/%d/%Y %H:%M')
			return dt

		return None


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

class NerrDate(object):
	def __init__(self, date_str):
		self._str = date_str
		self.dates = list()
		for dst in self._str.split(';'):
			dst_split = dst.split('-')
			start_str = dst_split[0].split()
			start_dt = datetime(int(start_str[1]),month(start_str[0]),1)
			end_dt = datetime.today()
			if len(dst_split) > 1 and len(dst_split[1]) > 0:
				end_str = dst_split[1].split()
				if len(end_str) == 2:
					end_dt = datetime(int(end_str[1]),month(end_str[0]),1)
				else:
					end_dt = datetime(int(end_str[0]),1,1)
			self.dates.append(start_dt)
			self.dates.append(end_dt)
		self.dates.sort()

	def get_start_date(self, obj=False):
		if obj == False:
			return self.dates[0].strftime("%m/%d/%Y")
		else:
			return self.dates[0]

	def get_latest_date(self, obj=False):
		if obj == False:
			i = len(self.dates) - 1
			return self.dates[i].strftime("%m/%d/%Y")
		else:
			return self.dates[i]
