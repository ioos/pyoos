import collections

class AsaList(object):

    @classmethod
    def flatten(cls, lst):
        """
            Returns Generator of non-iterable values
        """
        for x in lst:
            if not isinstance(x, collections.Iterable):
                yield x
            else:
                for x in AsaList.flatten(x):
                    yield x
