from pyoos.cdm.collections.feature_collection import FeatureCollection

class NestedPointCollection(FeatureCollection):
    """
        A collection of PointCollections
    """

    def subset(self, **kwargs):
        """
            by BBOX
            by Timerange

            @returns NestedPointCollection
        """

    def flatten(self):
        """
            return all PointCollections flattened into a single PointCollection

            @returns PointCollection
        """