from pyoos.cdm.collections.profile_collection import ProfileCollection

class Section(ProfileCollection):
    """
        A collection of profiles along a trajectory
    """

    def __init__(self, **kwargs):
        super(Section,self).__init__(**kwargs)
        self._type = "Section"

    def get_path(self):
        """
            Returns the nominal times of the profiles and the Points
            the profile was taken at.
        """
        return map(lambda x: [x.location, x.time], self._elements)