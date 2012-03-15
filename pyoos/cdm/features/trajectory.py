from pyoos.cdm.collections.point_collection import PointCollection

class Trajectory(PointCollection):
	"""
		A collection of Points along a 1 dimensional path, connected in space and time.
 		The Points are ordered in time (in other words, the time dimension must
 		increase monotonically along the trajectory).
	"""