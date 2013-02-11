from pyoos.cdm.collections.point_collection import PointCollection
from shapely.geometry import MultiPoint

class Station(PointCollection):
    """
        A collection of points at a single location
    """
    def __init__(self, **kwargs):
        super(Station,self).__init__(**kwargs)
        self._type = "timeSeries"
        self._properties = dict()
        self.uid = None
        self.name = None        
        self.description = None

    def get_location(self):
        return self._location
    def set_location(self, location):
        self._location = location

        # Sets the location of every Point in this Station if it is not already set
        for p in self._elements:
            try:
                assert p.location is not None
            except:
                p.location = self._location
        
    location = property(get_location, set_location)

    def get_uid(self):
        return self._uid
    def set_uid(self, uid):
        self._uid = uid
    uid = property(get_uid, set_uid)

    def get_name(self):
        return self._name
    def set_name(self, name):
        self._name = name
    name = property(get_name, set_name)

    def get_unique_members(self):
        all_members = (m for m in (e.members for e in self.elements))

        keys = ["name", "description", "standard", "unit"]
        mwhat = []
        for mg in all_members:
            for m in mg:
                mwhat.append( { key: m[key] for key in keys if key in m } )

        # Now unique them on name
        mwhat = { x['name']:x for x in mwhat }.values()

        return mwhat

    def get_description(self):
        return self._description
    def set_description(self, description):
        self._description = description
    description = property(get_description, set_description)

    def properties(self):
        """ General properties to store things about a station """
        return self._properties
    def set_property(self, prop, value):
        self._properties[prop] = value
    def get_property(self, prop):
        return self._properties.get(prop, None)

    def calculate_bounds(self):
        """
            Calculate the time_range, bbox, and size of this collection.
            Will scan all data.
            Ensures that .size, .bbox and .time_range return non-null.

            If the collection already knows its bbox; time_range; and/or size,
            they are recomputed.
        """ 
        self.location = self._location # To set locations for all points that don't have one
        stuff = map(lambda x: [x.time, x.location], self._elements)
        self.time_range = sorted(map(lambda x: x[0], stuff))
        points = map(lambda x: x[1], stuff)
        try:
            self.depth_range = sorted(map(lambda x: x[1].z, stuff))
        except:
            self.depth_range = None
        self.bbox = MultiPoint([self.location, self.location]).envelope
        self.size = len(self._elements)
