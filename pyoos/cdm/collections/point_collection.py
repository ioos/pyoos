from pyoos.cdm.collections.feature_collection import FeatureCollection
from shapely.geometry import MultiPoint
from shapely.geometry import Point

class PointCollection(FeatureCollection):
    """
        A collection of Points
    """

    def __init__(self, elements):
        self._elements = elements
        self._type = "Point"
        super(PointCollection,self).__init__()

    def get_time_range(self):
        """ 
            Requires a call to calculateBounds
        """        
        return self._time_range
    def set_time_range(self, time_range):
        self._time_range = time_range
    time_range = property(get_time_range, set_time_range)

    def get_depth_range(self):
        """ 
            Requires a call to calculateBounds
        """        
        return self._depth_range
    def set_depth_range(self, depth_range):
        self._depth_range = depth_range
    depth_range = property(get_depth_range, set_depth_range)

    def lower_left(self):
        return Point(self._bbox[0], self._bbox[1])
    def upper_right(self):
        return Point(self._bbox[2], self._bbox[3])
    def get_bbox(self):
        """ 
            Requires a call to calculateBounds
        """
        return self._bbox
    def set_bbox(self, bbox):
        self._bbox = bbox
    bbox = property(get_bbox, set_bbox)

    def get_size(self):
        """ 
            Requires a call to calculateBounds
        """        
        return self._size
    def set_size(self, size):
        self._size = size
    size = property(get_size, set_size)

    def calculateBounds(self):
        """
            Calculate the time_range, bbox, and size of this collection.
            Will scan all data.
            Ensures that .size, .bbox and .time_range return non-null.

            If the collection already knows its bbox; time_range; and/or size,
            they are not computed.
        """        
        points = map(lambda x: x.location, self._elements)
        self.bbox = MultiPoint(points).bounds
        self.time_range = sorted(map(lambda x: x.time, self._elements))
        self.depth_range = sorted(map(lambda x: x.location.z, self._elements))
        self.size = len(self._elements)
