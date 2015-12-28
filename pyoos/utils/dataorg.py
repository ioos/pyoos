from __future__ import (absolute_import, division, print_function)

def flatten_element(p):
    """
    Convenience function to return record-style time series representation
    from elements ('p') members in station element.
    member['standard'] is a standard_name parameter name, typically CF based.
    Ideally, member['value'] should already be floating point value,
    so it's ready to use.
    Useful with most pyoos collectors.
    """
    rd = {'time': p.time}
    for member in p.members:
        rd[member['standard']] = member['value']
    return rd
