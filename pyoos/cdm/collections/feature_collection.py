from shapely.geometry import Point

class FeatureCollection(object):
    """
        A collection of Features
        All Features in a FeatureCollection must be of the same type
    """

    def __init__(self, **kwargs):
        self.elements = kwargs.pop('elements', [])

    def set_type(self, type):
        self._type = type
    def get_type(self):
        return self._type
    type = property(get_type, set_type)

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
        return Point(self._bbox.bounds[0], self._bbox.bounds[1])
    def upper_right(self):
        return Point(self._bbox.bounds[2], self._bbox.bounds[3])
    def get_bbox(self):
        """ 
            Returns a Shapely Polygon object representing the bbox
            
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

    def add_element(self, element):
        self._elements.append(element)
    def set_elements(self, elements):
        self._elements = elements
    def get_elements(self):
        return self._elements
    elements = property(get_elements, set_elements)

    def __iter__(self):
        return iter(self.elements)