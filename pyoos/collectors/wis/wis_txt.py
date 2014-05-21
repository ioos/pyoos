from pyoos.collectors.collector import Collector
from datetime import datetime
import requests
import csv
import re

class WisTxt(Collector):
	def __init__(self, **kwargs):
		'''
		get the station list and create array of dicts, related to the staiton information
		links for station information are provided here: http://wis.usace.army.mil/Station_Info_Tables.shtml
		'''

		#url and file information
		base_url = "http://wis.usace.army.mil/"
		file_ext = ".txt"
		file_locations = ["atl","gom","pac","alaska","mich","huron","super","erie","ont"]
		wis_ext = "_wis"
		location_long_name = ["Atlantic","Gulf","Pacific","Alaska","Lake Michigan","Lake Huron","Lake Superior","Lake Erie","Lake Ontario"]

		#dict fields
		node_name = "name"
		node_lat = "lat"
		node_lon = "lon"
		node_depth = "depth"
		#uses the file location as its embedded in the data link
		node_location = "location"
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
					    row=row.split(",")
					    if ln_count > header_ln_count:
					        #set node data
					        node_data ={}
					        #set node location, used for url
					        node_data[node_location] = f
					        if len(row) ==  len(node_name_list.keys()):
					            #loop through the available mappings
					            for field_key in node_name_list.keys(): 
					                node_data[field_key] = row[node_name_list[field_key]]

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
		lists all available features
		'''
		return self.node_list

	def collect(self):
		'''
		Collect
		'''	
		raise StandardError("Not yet implemented....")	

	def raw(self, **kwargs):
		'''
		Raw
		'''
		raise StandardError("Not yet implemented....")

	def metadata(self, **kwargs):
		'''
		MetaData
		'''
		raise StandardError("Not yet implemented....")		
