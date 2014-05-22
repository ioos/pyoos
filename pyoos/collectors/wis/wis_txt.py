from pyoos.collectors.collector import Collector
from datetime import datetime
import requests
import csv
import re
from shapely.geometry import Polygon,Point,LineString

#dict fields
node_name = "name"
node_lat = "lat"
node_lon = "lon"
node_depth = "depth"
#uses the file location as its embedded in the data link
node_location = "location"
wave_dir = "WAVE DIR"
wind_speed = "WND SPD"
wind_dir = "WIND DIR"

class WisTxt(Collector):
	def __init__(self, **kwargs):		
		'''
		get the station list and create array of dicts, related to the staiton information
		links for station information are provided here: http://wis.usace.army.mil/Station_Info_Tables.shtml
		'''
		self.bbox = None
		self.start_time = None
		self.end_time = None
		self.stations_in_bbox = []

		#url and file information
		base_url = "http://wis.usace.army.mil/"
		file_ext = ".txt"
		file_locations = ["atl","gom","pac","alaska","mich","huron","super","erie","ont"]
		wis_ext = "_wis"
		location_long_name = ["Atlantic","Gulf","Pacific","Alaska","Lake Michigan","Lake Huron","Lake Superior","Lake Erie","Lake Ontario"]

		node_name_list = {node_name:0,node_lat:1,node_lon:2,node_depth:3}

		#loop through the files and parse all the nodes out
		node_list = []
		for f in file_locations:
			try:
				r = requests.get(base_url+f+wis_ext+file_ext)
				if r.status_code ==200:
					wis_data = r.text
					#split on new line
					wis_data = wis_data.split("\n")
					ln_count=0
					header_ln_count =1;
					for row in wis_data:
						ln_count+=1      
						row = row.strip()
						row = re.sub(' +', ',', row)
						row = row.split(",")
						if ln_count > header_ln_count:
							#set node data
							node_data ={}
							#set node location, used for url
							node_data[node_location] = f
							if len(row) ==  len(node_name_list.keys()):
								#loop through the available mappings
								for field_key in node_name_list.keys(): 
									data_string = row[node_name_list[field_key]]									
									node_data[field_key] = str(data_string)

							node_list.append(node_data)
					
				else:
					raise StandardError("could not connect to file "+f)
					pass
			except Exception, e:
				raise "could not connect to wis service:", e 
		#set to self param		
		self.node_list = node_list

	def list_variables(self):
		raise StandardError("Not yet implemented....")

	def list_features(self):
		'''
		lists all available features inside a bounding box
		'''
		if self.bbox is not None:
			poly = Polygon(self.bbox)
			#loop through the node list and see if the station is inside the bounding box of interest
			for node in self.node_list:			
				if len(node.keys()) == 5:					
					lat = float(node[node_lat])
					lon = float(node[node_lon])
					ll_point = Point(lat,lon)
					is_station_contained = poly.contains(ll_point)					
					if is_station_contained is True:	
						self.stations_in_bbox.append(node)

			return self.stations_in_bbox		
		else:
			raise StandardError("no bounding box selected....")	

	def collect(self):
		'''
		Collect, not used as yet
		'''	
		raise StandardError("Not yet implemented....")	

	def raw(self, **kwargs):
		'''
		Raw, gets the available data from a set of requested node
		'''
		if node_name in kwargs.keys():	
			if len(self.stations_in_bbox)>=1:
				for node in self.stations_in_bbox:					
					if node[node_name] == kwargs[node_name]:
						return self.get_raw_data(node)	
			else:
				raise StandardError("No stations found...")						

		else:			
			raise StandardError("Not yet implemented....")		

	def get_raw_data(self,node):		
		'''
		get_raw_data, uses the node information to request and parse a wis data product
		'''
		#build url
		url = "http://wis.usace.army.mil/"+node[node_location]+"/XTRMS/ST"+node[node_name]+"_MEAN_MAX.TXT"
		print url
		r = requests.get(url,timeout=2)
		raw_data = r.text.split("\n")
		header_ln_count =3;
		ln_count =0
		headers = []
		node_data = {}
		for row in raw_data:			
			ln_count+=1 
			#remove prevailing and trailing whitespace
			row = row.strip()					
			if ln_count > header_ln_count:
				row = self.split_row(row)

				#get the data
				idx = 0				
				if len(headers) == len(row):
					for h in headers:
						node_data[h].append(row[idx])
						idx+=1

			elif ln_count == header_ln_count:
				#replace data fields that do not match
				row = row.replace(wave_dir,"WAVE_DIR")
				row = row.replace(wind_dir,"WIND_DIR")
				row = row.replace(wind_speed,"WIND_SPD")
				row = self.split_row(row)
				#get the headers
				headers = row					
				for h in headers:
					node_data[h] = []

		#return the data			
		return node_data			

	def split_row(self,row):
		#replace all spaces with one comma
		row = re.sub(' +', ',', row)
		#split the data
		row=row.split(",")
		return row		

	def metadata(self, **kwargs):
		'''
		MetaData, lists all nodes available 
		'''
		return self.node_list
