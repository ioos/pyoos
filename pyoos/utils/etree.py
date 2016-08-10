from __future__ import (absolute_import, division, print_function)
import six
import inspect

# Makes etree, ElementType, and ParseError availablefrom either `lxml `or `xml`.
try:
    from lxml import etree
    from lxml.etree import ParseError
    ElementType = etree._Element
except ImportError:
    try:
        # Python 2.x/3.x with ElementTree included.
        import xml.etree.ElementTree as etree

        try:
            from xml.etree.ElementTree import ParseError
        except ImportError:
            from xml.parsers.expat import ExpatError as ParseError

        if hasattr(etree, 'Element') and inspect.isclass(etree.Element):
            # Python 3.4, 3.3, 2.7.
            ElementType = etree.Element
        else:
            # Python 2.6.
            ElementType = etree._ElementInterface

    except ImportError:
        try:
            # Python < 2.5 with ElementTree installed.
            import elementtree.ElementTree as etree
            ParseError = StandardError
            ElementType = etree.Element
        except ImportError:
            raise RuntimeError('You need either lxml or ElementTree to use pyoos!')
