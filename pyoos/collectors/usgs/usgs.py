from pyoos.collectors.collector import Collector
from datetime import datetime
from urllib2 import urlopen, Request, HTTPError
from pyoos.parsers.usgs.usgs_waterml import USGSParser

class USGSCollector(Collector):
	def __init__(self, **kwargs):
		super(USGSCollector,self).__init__()
		self._usgs_http = 'http://waterservices.usgs.gov/nwis/iv'
		self._parser = USGSParser()

	def get_stations_by_bbox(self,north,south,east,west,period_days=None,period_hours=None,startDT=None,endDT=None):
		"""
			retrieves a StationCollection object from USGS determined by the boundaries given
			Note: according to the USGS web site, the product of the range of latitude and longitude cannot exceed 25 degrees
			- north: northern latitude (in decimal or string)
			- south: southern latitude (in decimal or string)
			- east: eastern longitude (in decimal or string)
			- west: western longitude (in decimal or string)
			(optional)
			Note: If none of the below are used, then the lastest values are retrieved.
			Note: site local time is used, timezone cannot be specified in request
			- period_days: the period of time to go back in days
			- period_hours: the period of time to go back in hours. Note: period_days superceeds this argument (one or the other, not both)
			- startDT: The start datetime following ISO-8601. Note: period_days, period_hours superceeds this argument.
			- endDT: The end datetime following ISO-8601. Note: this must be specified with startDT or it will not be used; also is superceeded by period
		"""
		# determine what arguments are used
		if north is None or south is None or east is None or west is None:
			raise ValueError("north, sourth, east and west must be specified for bbox")

		if startDT is not None:
			if not isinstance(startDT, datetime):
				raise ValueError("startDT is specified, but is not of instance datetime.datetime")
			if endDT is not None and not isinstance(endDT, datetime):
				raise ValueError("endDT is specified, but is not of instance datetime.datetime")

		bBox = str('%s,%s,%s,%s' % (str(west),str(south),str(east),str(north)))

		args = dict(bBox=bBox)

		if period_days is not None:
			args['period'] = str('P%sD' % (str(period_days)))
		elif period_hours is not None:
			args['period'] = str('PT%sH' % (str(period_hours)))
		elif startDT is not None:
			args['startDT'] = startDT.strftime('%Y-%m-%dT%H:%M')
			if endDT is not None:
				args['endDT'] = endDT.strftime('%Y-%m-%dT%H:%M')

		response = self.__request_from_usgs(args)

		return self._parser.parse_response(response)

	def get_stations_by_state(self,state_code,period_days=None,period_hours=None,startDT=None,endDT=None):
		"""
			retrieves a StationCollection object from USGS, determined by the state code 
			- state_code: an USPS postal service (2-character) state code
			(optional)
			Note: If none of the below are used, then the lastest values are retrieved.
			Note: site local time is used, timezone cannot be specified in request
			- period_days: the period of time to go back in days
			- period_hours: the period of time to go back in hours. Note: period_days superceeds this argument (one or the other, not both)
			- startDT: The start datetime following ISO-8601. Note: period_days, period_hours superceeds this argument.
			- endDT: The end datetime following ISO-8601. Note: this must be specified with startDT or it will not be used; also is superceeded by period
		"""
		# determine valid parameters
		if state_code is None or not isinstance(state_code, str):
			raise ValueError("state_code was expected as a string value")

		args = dict(stateCd=state_code)

		if period_days is not None:
			args['period'] = str('P%sD' % (str(period_days)))
		elif period_hours is not None:
			args['period'] = str('PT%sH' % (str(period_hours)))
		elif startDT is not None:
			args['startDT'] = startDT.strftime('%Y-%m-%dT%H:%M')
			if endDT is not None:
				args['endDT'] = endDT.strftime('%Y-%m-%dT%H:%M')

		response = self.__request_from_usgs(args)

		return self._parser.parse_response(response)

	def get_station(self,site,period_days=None,period_hours=None,startDT=None,endDT=None):
		"""
			retrieves a Station object from USGS, determined by the site id
			(optional)
			Note: If none of the below are used, then the lastest values are retrieved.
			Note: site local time is used, timezone cannot be specified in request
			- period_days: the period of time to go back in days
			- period_hours: the period of time to go back in hours. Note: period_days superceeds this argument (one or the other, not both)
			- startDT: The start datetime following ISO-8601. Note: period_days, period_hours superceeds this argument.
			- endDT: The end datetime following ISO-8601. Note: this must be specified with startDT or it will not be used; also is superceeded by period
		"""
		# determine params
		if site is None:
			raise ValueError("site is expected to be not None")

		site_p = ""
		if isinstance(site, list):
			for item in site:
				site_p += str(item) + ","
		else:
			site_p = str(site)

		args = dict(site=site_p)

		if period_days is not None:
			args['period'] = str('P%sD' % (str(period_days)))
		elif period_hours is not None:
			args['period'] = str('PT%sH' % (str(period_hours)))
		elif startDT is not None:
			args['startDT'] = startDT.strftime('%Y-%m-%dT%H:%M')
			if endDT is not None:
				args['endDT'] = endDT.strftime('%Y-%m-%dT%H:%M')

		response = self.__request_from_usgs(args)

		return self._parser.parse_response(response)

	def __request_from_usgs(self,args):
		if args is None or not isinstance(args, dict):
			raise ValueError("args was expected to be non-None and of type dict")

		url = self._usgs_http
		# add all of the arguments
		query = "?"
		for item in args.items():
			query += str('%s=%s&' % (str(item[0]),str(item[1])))
		url += query

		try:
			req = urlopen(Request(url))
		except:
			raise
			return None

		resp = req.read()
		req.close()

		return resp
