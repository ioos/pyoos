from pyoos.cdm.features.feature import Feature

class Point(Feature):
    """
        A collection of observations at one time and location.
        ie. An instantaneous reading of multiple parameters from a sensor
    """

    def __init__(self):
        self._memberNames = []
        self._members = []
        self._type = "Point"
        return None

    def get_location(self):
        """
            A Shapely Point object (x,y,z) in the cartesian plane
        """
        return self._location
    def set_location(self, location):
        self._location = location
    location = property(get_location, set_location)

    def get_time(self):
        """
            The observation time
        """
        return self._time
    def set_time(self, time):
        self._time = time
    time = property(get_time, set_time)

    def add_member(self, member):
        self._members.append(member)
        self._memberNames.append(member['name'])

    def get_member(self, **kwargs):
        """
            Get Member by variable name
        """
        return self._members[self._memberNames.index(kwargs.get('name'))]

    def set_members(self, members):
        self._members = members
    def get_members(self):
        return self._members
    members = property(get_members, set_members)
