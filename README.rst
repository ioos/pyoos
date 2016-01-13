Pyoos - A Python library for collecting Met/Ocean observations
==============================================================

.. image:: https://travis-ci.org/ioos/pyoos.svg?branch=master
   :target: https://travis-ci.org/ioos/pyoos
   :alt: Build_Status


*Note: Pyoos is very much a work in progress and should considered
experimental until a 1.0 release is made!*

Pyoos attempts to fill the need for a high level data collection library
for met/ocean data publically available through many different websites
and webservices.

Pyoos will collect and parse the following data services into the
`Paegan <https://github.com/asascience-open/paegan#paegan---the-python-cdm-for-metocean-data>`__
Discrete Geometry CDM:

-  IOOS SWE SOS 1.0 Services
-  ex. `NcSOS <https://github.com/asascience-open/ncsos>`__ instance:
   `sos.maracoos.org/stable/sos/wflow700-agg.ncml <http://sos.maracoos.org/stable/sos/wflow700-agg.ncml>`__
-  ex. `IOOS 52N <http://ioossos.axiomalaska.com/>`__ instance:
   `ioossos.axiomalaska.com/52n-sos-ioos-stable <http://ioossos.axiomalaska.com/52n-sos-ioos-stable/>`__
-  NERRS Observations - SOAP
-  NDBC Observations - SOS
-  CO-OPS Observations - SOS
-  STORET Water Quality - WqxOutbound via REST (waterqualitydata.us)
-  USGS NWIS Water Quality - WqxOutbound via REST (waterqualitydata.us)
-  USGS Instantaneous Values - WaterML via REST
-  NWS AWC Observations - XML via REST (http://www.aviationweather.gov)
-  HADS (http://www.nws.noaa.gov/oh/hads/ - limited to 7 day rolling
   window of data)

Common Interface
----------------

Filtering data
~~~~~~~~~~~~~~

Geo
^^^

Filter by bbox
''''''''''''''

.. code:: python

    # (minx, miny, maxx, maxy)
    collector.filter(bbox=(-74, 30, -70, 38))

Time
^^^^

Filter from a datetime (the 'start' parameter)
''''''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    from dateime import dateime, timedelta
    collector.filter(start=datetime.utcnow() - timedelta(hours=1))

Filter until a datetime (the 'end' parameter)
'''''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    from dateime import dateime
    collector.filter(end=datetime.utcnow())

Filter a datetime range (both 'start' and 'end' parameters)
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    from dateime import dateime, timedelta
    collector.filter(start=datetime.utcnow - timedelta(hours=24), end=datetime.utcnow())

Feature(s)
^^^^^^^^^^

It is highly dependent on the data provider how they identify unique
features/stations/objects.
Pyoos does its best job to figure out what you are passing in. For
example,
you may pass WMO ID's to the NDBC collector and Pyoos will request the
correct complete URN to the NDBC SOS.

Retrieve a list of unique features available to filter
''''''''''''''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    collector.list_features()

Filter by unique feature
''''''''''''''''''''''''

.. code:: python

    # Any iterable of strings
    collector.filter(features=["21KY-BSW004"])

Variable(s)
^^^^^^^^^^^

Pyoos does its best job to format any string into the correct format
for the actual request. For example,
you may pass typical standard\_name string from CF-1.6 to the NDBC
collector and Pyoos will turn it into a complete MMI URI.

Retreive a list of unique variables available to filter
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    collector.list_variables()

Filter by variable name
'''''''''''''''''''''''

.. code:: python

    # Any iterable of strings
    collector.filter(variables=["sea_water_temperature"])

Clear active filters
^^^^^^^^^^^^^^^^^^^^

.. code:: python

    collector.clear()

Filter Chaining
---------------

You may chain many ``filter`` calls together (it returns a collector
object)

.. code:: python

    collection.filter(bbox=(-74, 30, -70, 38)).filter(end=datetime.utcnow())

You may also combine many filter types into one call to ``filter``

.. code:: python

    collection.filter(bbox=(-74, 30, -70, 38), end=datetime.utcnow())

Get Data
--------

As Paegan CDM objects
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    collector.collect()

As raw response from provider
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    collector.raw()

Specific functionality
----------------------

Each collector may implement a set of functions specific to that
collection. Please see the Wiki for an explanation of this type of
functionality.

Setup
-----

You are using ``virtualenv``, right?

#. Install
   `virtualenv-burrito <https://github.com/brainsik/virtualenv-burrito>`__
#. Create virtualenv named "pyoos-dev":
   ``mkvirtualenv -p your_python_binary pyoos-dev``
#. Start using your new virtualenv: ``workon pyoos-dev``

Installation
------------

Pyoos requires python 2.7.x and is available on PyPI.

The best way to install Pyoos is through pip:

.. code:: bash

    pip install pyoos

Pyoos requires the following python libraries which will be downloaded
and installed through ``pip``:

-  Paegan>=0.9.9
-  numpy>=1.7.0
-  scipy
-  netCDF4>=1.0.2
-  Shapely>=1.2.15
-  pytz
-  python-dateutil>=1.5
-  OWSLib (install from git with
   ``pip install git+http://github.com/geopython/OWSLib.git``)
-  requests
-  Fiona==0.16.1
-  beautifulsoup4==4.2.1
-  lxml>=3.2.0

If your NetCDF4 and HDF5 libraries are in non-typical locations, you
will need to pass the locations to the ``pip`` command:

.. code:: bash

    NETCDF4_DIR=path HDF5_DIR=path pip install pyoos

There seems to be a problem installing numpy through ``pip`` dependency
chains so you may need to install numpy before doing any of the above:

.. code:: bash

    pip install numpy==1.7.0

Roadmap
-------

-  Development of a standardized Metadata concept, possibly through
   SensorML and/or ISO 19115-2

Use Cases
---------

Submit a PR with your use case!

Troubleshooting
---------------

There is a Google Groups mailing list for pyoos:
https://groups.google.com/forum/#!forum/pyoos

If you are having trouble getting any of the pyoos functionality to
work, try running the tests:

.. code:: bash

    git clone git@github.com:asascience-open/pyoos.git
    cd pyoos
    python setup.py test

Contributors
------------

-  Kyle Wilcox kyle@axiomdatascience.com
-  Sean Cowan scowan@asascience.com
-  Alex Crosby acrosby@asascience.com
-  Dave Foster dave@axiomdatascience.com
-  Filipe Pires Alvarenga Fernandes ocefpaf@gmail.com

Copyright and licence
---------------------

Copyright (C) 2012-2016 RPS ASA

This file is part of Pyoos.

Pyoos is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pyoos is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License
along with Pyoos. If not, see http://www.gnu.org/licenses/.
