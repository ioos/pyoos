try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5 with ElementTree included
        import xml.etree.ElementTree as etree
    except ImportError:
        try:
            # Python < 2.5 with ElementTree installed
            import elementtree.ElementTree as etree
        except ImportError:
            raise RuntimeError('You need either lxml or ElementTree')