from pyoos.cdm.collections.feature_collection import FeatureCollection
from shapely.geometry import MultiPoint
from datetime import datetime
import sys

class PointCollection(FeatureCollection):
    """
        A collection of Points
    """

    def __init__(self, **kwargs):
        super(PointCollection,self).__init__(**kwargs)

    def filter_by_time(self, starting, ending):
        if not isinstance(starting, datetime) or not isinstance(ending, datetime):
            raise ValueError("Starting and ending must both be datetime objects")
        return (e for e in self.elements if starting <= e.time <= ending)

    def filter_by_variable(self, variable, elements=None):
        if elements is None:
            elements = self.elements

        return (m for m in elements for h in m.members if h.get("name","") == variable or h.get("standard","") == variable)

    def calculate_bounds(self):
        """
            Calculate the time_range, bbox, and size of this collection.
            Will scan all data.
            Ensures that .size, .bbox and .time_range return non-null.

            If the collection already knows its bbox; time_range; and/or size,
            they are recomputed.
        """ 
        stuff = map(lambda x: [x.time, x.location], self._elements)
        self.time_range = sorted(map(lambda x: x[0], stuff))
        points = map(lambda x: x[1], stuff)

        try:
            filtered_stuff = self.__filter_depths(stuff)
            self.depth_range = sorted(map(lambda x: x[1].z, filtered_stuff))
        except:
            self.depth_range = None

        try:
            self.bbox = MultiPoint(points).envelope
        except:
            self.bbox = None
            
        self.size = len(self._elements)


    def __filter_depths(self, list_to_filter):
        retval = list()
        for item in list_to_filter:
            try:
                getz = item[1].z
                retval.append(item)
            except:
                pass # don't do anything

        return retval
