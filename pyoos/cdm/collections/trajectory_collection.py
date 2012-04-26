from pyoos.cdm.collections.nested_point_collection import NestedPointCollection

class TrajectoryCollection(NestedPointCollection):
    """
        A collection of Trajectories
    """

    def __init__(self, **kwargs):
        super(TrajectoryCollection,self).__init__(**kwargs)
        