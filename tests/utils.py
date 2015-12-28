from __future__ import (absolute_import, division, print_function)

import os


def resource_file(filepath):
    return os.path.join(test_directory(), 'resources', filepath)


def test_directory():
    """Helper function to return path to the tests directory"""
    return os.path.dirname(__file__)
