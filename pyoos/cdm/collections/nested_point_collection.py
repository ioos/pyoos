from pyoos.cdm.collections.feature_collection import FeatureCollection
from pyoos.cdm.collections.point_collection import PointCollection
from pyoos.cdm.features.point import Point
import itertools
import collections
from pyoos.utils.asalist import AsaList

class NestedPointCollection(FeatureCollection):
    """
        A collection of PointCollections
    """

    def __init__(self, **kwargs):
        super(NestedPointCollection,self).__init__(**kwargs)

    def calculate_bounds(self):
        """
            Calculate the time_range, bbox, and size of this collection.
            Will scan all data.
            Ensures that .size, .bbox and .time_range return non-null.

            If the collection already knows its bbox; time_range; and/or size,
            they are recomputed.
        """ 
        single_point_collection = PointCollection(elements=list(AsaList.flatten(self)))
        single_point_collection.calculate_bounds()
        self.bbox = single_point_collection.bbox
        self.time_range = single_point_collection.time_range
        self.depth_range = single_point_collection.depth_range
        self._point_size = single_point_collection.size
        self.size = len(self._elements)
        

    def flatten(self):
        """
            Returns a Generator of Points that are part of this collection
        """
        return AsaList.flatten(self)

    def get_point_size(self):
        """
            Returns the number of actual Points in this NestedPointCollection

            Ex.  pc = 10 profiles with 20 bins each will return 200
                 pc.size = 10
                 pc.point_size = 200
        """
        return self._point_size
    point_size = property(get_point_size, None)