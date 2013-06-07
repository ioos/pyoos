# Pyoos - A Python library for collecting Met/Ocean observations

*Note: Pyoos is very much a work in progress and should considered experimental until a 1.0 release is made!*

Pyoos attempts to fill the need for a high level data collection library for met/ocean data publically available through many different websites and webservices.

Pyoos will collect and parse the following data services into the [Paegan](https://github.com/asascience-open/paegan#paegan---the-python-cdm-for-metocean-data) Discrete Geometry CDM:

* NERRS Observations - SOAP
* NDBC Observations - IOOS SWE SOS 1.0
* CO-OPS Observations - IOOS SWE SOS 1.0
* STORET Water Quality - WqxOutbound via REST (waterqualitydata.us)
* USGS NWIS Water Quality - WqxOutbound via REST (waterqualitydata.us)
* USGS Instantaneous Values - WaterML via REST


## Common Interface

### Filtering data

#### Geo
##### Filter by bbox
```python
# (minx, miny, maxx, maxy)
collector.filter(bbox=(-74, 30, -70, 38))
```
#### Time

##### Filter from a datetime (the 'start' parameter)
```python
from dateime import dateime, timedelta
collector.filter(start=datetime.utcnow() - timedelta(hours=1))
```
##### Filter until a datetime (the 'end' parameter)
```python
from dateime import dateime
collector.filter(end=datetime.utcnow())
```

##### Filter a datetime range (both 'start' and 'end' parameters)
```python
from dateime import dateime, timedelta
collector.filter(start=datetime.utcnow - timedelta(hours=24), end=datetime.utcnow())
```

#### Feature(s)
It is highly dependent on the data provider how they identify unique features/stations/objects.
Pyoos does its best job to figure out what you are passing in.  For example,
you may pass WMO ID's to the NDBC collector and Pyoos will request the correct complete URN to the NDBC SOS.

##### Retrieve a list of unique features available to filter
```python
collector.list_features()
```
##### Filter by unique feature
```python
# Any iterable of strings
collector.filter(features=["21KY-BSW004"])
```

#### Variable(s)
Pyoos does its best job to format any string into the correct format for the actual request.  For example,
you may pass typical standard_name string from CF-1.6 to the NDBC collector and Pyoos will turn it into a complete MMI URI.

##### Retreive a list of unique variables available to filter
```python
collector.list_variables()
```

##### Filter by variable name
```python
# Any iterable of strings
collector.filter(variables=["sea_water_temperature"])
```

#### Clear active filters
```python
collector.clear()
```

## Filter Chaining
You may chain many `filter` calls together (it returns a collector object)
```python
collection.filter(bbox=(-74, 30, -70, 38)).filter(end=datetime.utcnow())
```
You may also combine many filter types into one call to `filter`
```python
collection.filter(bbox=(-74, 30, -70, 38), end=datetime.utcnow())
```

## Get Data

### As Paegan CDM objects
```python
collector.collect()
```

### As raw response from provider
```python
collector.raw()
```


## Specific functionality

Each collector may implement a set of functions specific to that collection.  Please see the Wiki for an explanation of this type of functionality.


## Setup
You are using `virtualenv`, right?

1. Install [virtualenv-burrito](https://github.com/brainsik/virtualenv-burrito)
2. Create virtualenv named "pyoos-dev": `mkvirtualenv -p your_python_binary pyoos-dev`
3. Start using your new virtualenv: `workon pyoos-dev`


## Installation
Pyoos requires python 2.7.x and is available on PyPI.

The best way to install Pyoos is through pip:

```bash
pip install pyoos
```

Pyoos requires the following python libraries which will be downloaded and installed through `pip`:

* Paegan>=0.9.6
* OWSLib (custom fork... but will be intergrated soon!)
* Shapely>=1.2.17
* pytz>=2012h
* python-dateutil>=2.1
* requests
* lxml

If your NetCDF4 and HDF5 libraries are in non-typical locations, you will need to pass the locations to the `pip` command:
```bash
NETCDF4_DIR=path HDF5_DIR=path pip install pyoos
```

There seems to be a problem installing numpy through `pip` dependency chains so you may need to install numpy before doing any of the above:

```bash
pip install numpy==1.6.2
```

## Roadmap
* Development of a standardized Metadata concept, possibly through SensorML and/or ISO 19115-2


## Use Cases
Submit a PR with your use case!


## Troubleshooting
If you are having trouble getting any of the pyoos functionality to work, try running the tests:

```bash
git clone git@github.com:asascience-open/pyoos.git
cd pyoos
python setup.py test
```

## Contributors
* Kyle Wilcox <kwilcox@asascience.com>
* Sean Cowan <scowan@asascience.com>
* Alex Crosby <acrosby@asascience.com>

