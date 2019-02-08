from __future__ import absolute_import, division, print_function

# Package level logger
import logging

try:
    # Python >= 2.7
    from logging import NullHandler
except ImportError:
    # Python < 2.7
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logger = logging.getLogger("pyoos")
logger.addHandler(logging.NullHandler())

from ._version import get_versions  # noqa

__version__ = get_versions()["version"]
del get_versions
