Pyoos - A Python library for collecting Met/Ocean observations
===========

*Note: Pyoos is very much a work in progress and should considered experimental until a 1.0 release is made!*

Pyoos attempts to fill the need for a high level data collection library for met/ocean data publically available through many different websites and webservices.

Pyoos will collect and parse the following data services into the [Paegan](https://github.com/asascience-open/paegan#paegan---the-python-cdm-for-metocean-data) Discrete Geometry CDM:

* NERRS Observations - SOAP
* NDBC Observations - IOOS SWE SOS 1.0
* CO-OPS Observations - IOOS SWE SOS 1.0
* STORET Water Quality - WqxOutbound via REST (waterqualitydata.us)
* USGS NWIS Water Quality - WqxOutbound via REST (waterqualitydata.us)
* USGS Instantaneous Values - WaterML via REST

Common Query Interface
------------------
Coming Soon!

Setup
------------------
You are using `virtualenv`, right?

1. Install [virtualenv-burrito](https://github.com/brainsik/virtualenv-burrito)
2. Create virtualenv named "pyoos-dev": `mkvirtualenv -p your_python_binary pyoos-dev`
3. Start using your new virtualenv: `workon pyoos-dev`

Installation
-------------
Pyoos requires python 2.7.x and is available on PyPI.

The best way to install Pyoos is through pip:

```bash
pip install pyoos
```

Pyoos requires the following python libraries which will be downloaded and installed through `pip`:

* [Paegan](https://github.com/asascience-open/paegan#paegan---the-python-cdm-for-metocean-data)>=0.9.6
* OWSLib (custom fork... but will be intergrated soon!)
* Shapely>=1.2.17
* pytz>=2012h
* python-dateutil>=2.1
* requests

If your NetCDF4 and HDF5 libraries are in non-typical locations, you will need to pass the locations to the `pip` command:
```bash
NETCDF4_DIR=path HDF5_DIR=path pip install pyoos
```

There seems to be a problem installing numpy through `pip` so you may need to install numpy before doing any of the above:

```bash
pip install numpy==1.6.2
```

Roadmap
--------
* Common collector interface for all data queries:
  * Geospatial subsetting
  * Temporal subsetting
  * Variable subsetting
  * Query by unique station ID
* Integration of an IOOS Metadata class

Troubleshooting
---------------
If you are having trouble getting any of the pyoos functionality to work, try running the tests:

```bash
git clone git@github.com:asascience-open/pyoos.git
cd pyoos
python setup.py test
```

Contributors
----------------
* Kyle Wilcox <kwilcox@asascience.com>
* Alexander Crosby <acrosby@asascience.com>
* Sean Cowan <scowan@asascience.com>

