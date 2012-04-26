from pyoos.cdm.collections.nested_point_collection import NestedPointCollection
from shapely.geometry import MultiPoint
from shapely.geometry import Point

class ProfileCollection(NestedPointCollection):
    """
        A collection of Profiles
    """

    def __init__(self, **kwargs):
        super(ProfileCollection,self).__init__(**kwargs)