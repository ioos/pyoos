class Feature(object):

	def __init__(self):
		return None

	def get_type(self):
		return self._type
	def set_type(self, type):
		self._type = value
	type = property(get_type, set_type)

	def get_title(self):
		return self._location
	def set_title(self, title):
		self._title = title
	title = property(get_title, set_title)

	def get_description(self):
		return self._description
	def set_description(self, description):
		self._description = description
	description = property(get_description, set_description)

	def get_daterange(self):
		return self._daterange
	def set_daterange(self, daterange):
		self._daterange = daterange
	daterange = property(get_daterange, set_daterange)

