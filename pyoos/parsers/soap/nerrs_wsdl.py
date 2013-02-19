from pyoos.utils.etree import etree
from owslib.util import nspath, testXMLValue
from datetime import date, MINYEAR, datetime

SOAPENV = 'http://schemas.xmlsoap.org/soap/envelope/'
NS1 = 'http://webservices2'

def nsp(element_tag, namespace):
	return nspath(element_tag, namespace=namespace)

class WsdlReply(object):

	def __init__(self, wsdl_response):
		if isinstance(wsdl_response, str) or isinstance(wsdl_response, unicode):
			try:
				self._root = etree.fromstring(wsdl_response)
			except Exception, e:
				self._root = etree.fromstring(wsdl_response[38:])

		if hasattr(self._root, 'getroot'):
			self._root = self._root.getroot()

	def get_stations(self, **kwargs):
		global SOAPENV, NS1
		retval = list()
		try:
			nerrFilter = False
			body = nsp('Body', SOAPENV)
			resp = nsp('exportStationCodesXMLNewResponse', NS1)

			body = self._root.find(body)
			resp = body.find(resp)

			if resp is None:
				resp = nsp('NERRFilterStationCodesXMLNewResponse', NS1)
				resp = body.find(resp)

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
			pass

		if len(retval) < 1:
			retval = None

		if retval is None and nerrFilter == True:
			raise ValueError(str('No stations associated with given site_id'))
		elif retval is None and kwargs.get('station_code') is not None:
			raise ValueError(str('Unable to find station with code: %s' % (kwargs.get('station_code'))))

		return retval

	def get_data_single_param(self, **kwargs):
		global SOAPENV, NS1
		retval = NerrDataCollection()

		try:
			body = nsp('Body', SOAPENV)
			resp = nsp('exportSingleParamXMLNewResponse', NS1)
			ret = 'exportSingleParamXMLNewReturn'

			body = self._root.find(body)
			resp = body.find(resp)
			ret = resp.find(ret)
			retData = ret.find('returnData')

			for data in retData.findall('data'):
				retval.add_data(NerrStationData(data))
		except:
			retval = None
			pass

		return retval

	def get_data_all_params(self, **kwargs):
		global SOAPENV, NS1
		retval = NerrDataCollection()

		try:
			body = nsp('Body', SOAPENV)
			resp = nsp('exportAllParamsXMLNewResponse', NS1)
			ret = 'exportAllParamsXMLNewReturn'

			body = self._root.find(body)
			resp = body.find(resp)
			ret = resp.find(ret)
			retData = ret.find('returnData')

			for data in retData.findall('data'):
				retval.add_data(NerrStationData(data))
		except:
			retval = None
			raise

		return retval

	def get_data_date_range(self, **kwargs):
		global SOAPENV, NS1
		retval = NerrDataCollection()

		try:
			body = nsp('Body', SOAPENV)
			resp = nsp('exportAllParamsDateRangeXMLNewResponse', NS1)
			ret = 'exportAllParamsDateRangeXMLNewReturn'

			body = self._root.find(body)
			resp = body.find(resp)
			ret = resp.find(ret)
			retData = ret.find('returnData')

			for data in retData.findall('data'):
				retval.add_data(NerrStationData(data))
		except:
			retval = None
			raise

		if len(retval) < 1:
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

	def get_values(self, param=None, datetime=None):
		if param is None:
			param = self.__params()[0]

		if datetime is None:
			retval = list()
			for data in self._data:
				retval.append(data.get_value(param))
			return retval

		if datetime is not None:
			retval = list()
			for data in self._data:
				if data.is_datetime(datetime):
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
		hr = 0
		mn = 0
		#date
		d_str = dt_split[0].split('/')
		mth = int(d_str[0])
		day = int(d_str[1])
		yr = int(d_str[2])
		if len(dt_split) > 1:
			#time
			t_str = dt_split[1].split(':')
			hr = int(t_str[0])
			mn = int(t_str[1])

		dt = datetime(yr,mth,day,hr,mn)

		if hr == 0 and mn == 0:
			# compare dates
			# print str('comparing: %s - %s' % (dt.date().strftime('%m/%d/%Y'), self.timestamp.get_local_date()))
			if dt.date() < self.timestamp._local_dt.date() or dt.date() > self.timestamp._local_dt.date():
				return False
		else:
			# compare date times
			#print str('comparing: %s - %s' % (dt.strftime('%m/%d/%Y %H:%M'), self.timestamp.get_local_datetime()))
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
			dt_split = dt_str.split()
			sdate = dt_split[0]
			stime = dt_split[1]
			t_split = stime.split(':')
			hr = int(t_split[0])
			mn = int(t_split[1])
			d_split = sdate.split('/')
			mnth = int(d_split[0])
			day = int(d_split[1])
			yr = int(d_split[2])
			dt = datetime(yr,mnth,day,hr,mn)
			return dt

		return None


class NerrStation(object):
	def __init__(self, data_root):
		self._root = data_root
		# parse info
		#nameing
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

	def parse_date(self, date):
		"""
			dates are handed in looking like: Month Year-Month Year-Month
			ex: Jun 1996-Dec 2001
			dates can also be ongoing, resulting in
			ex: Jan 2002-
		"""
		now = today.today()
		split_date = date.split('-')
		# index 0 is start, index 1 is end
		start_date = split_date[0].split()
		retval = dict()
		retval['start_date'] = month(start_date[0]) + start_date[1]
		if len(split_date) > 1 and split_date[1] is not '':
			end_date = split_date[1].split()
			retval['end_date'] = month(end_date[0]) + end_date[1]
		else:
			retval['end_date'] = str(now.month) + "/" + str(now.day) + "/" + str(now.year)
		return retval

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
		self.min_date = date.today()
		self.max_date = date(MINYEAR,1,1)
		for dst in self._str.split(';'):
			dst_split = dst.split('-')
			start = dst_split[0].split()
			start_dt = date(int(start[1]), month(start[0]), 1)
			if self.min_date > start_dt:
				self.min_date = start_dt
			end_dt = date.today()
			if len(dst_split) > 1 and dst_split[1] != '':
				end = dst_split[1].split()
				if len(end) > 1:
					end_dt = date(int(end[1]), month(end[0]),1)
				else:
					end_dt = date(int(end[0]),1,1)
			if end_dt > self.max_date:
				self.max_date = end_dt
			self.dates.append(dict(start_date=start_dt,end_date=end_dt))

	def get_start_date(self, obj=False):
		if obj == False:
			return self.min_date.strftime("%m/%d/%Y")
		else:
			return self.min_date

	def get_latest_date(self, obj=False):
		if obj == False:
			return self.max_date.strftime("%m/%d/%Y")
		else:
			return self.max_date




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
