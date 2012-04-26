from pyoos.cdm.collections.point_collection import PointCollection

class Profile(PointCollection):
    """
        A collection of points along a vertical (z) access
        ie. A single profile from an ADCP or CTD

        A profile has a nominal lat/lon and time.
        Actual time may be constant, or vary with z.
        The z coordinates are monotonic, and may be increasing or decreasing.
    """
    def __init__(self, **kwargs):
        super(Profile,self).__init__(**kwargs)
        self._type = "Profile"

    def get_location(self):
        return self._location
    def set_location(self, location):
        self._location = location
    location = property(get_location, set_location)

    def get_time(self):
        """
            Nominal time of the profile.  This is usually the first time a reading was taken,
            since a profile's time can be contant of vary with z.
        """
        return self._time
    def set_time(self, time):
        self._time = time
    time = property(get_time, set_time)