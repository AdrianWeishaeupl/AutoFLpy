========
AutoFLpy
========


.. image:: https://img.shields.io/pypi/v/autoflpy.svg
        :target: https://pypi.python.org/pypi/autoflpy

.. image:: https://img.shields.io/travis/AdrianWeishaeupl/autoflpy.svg
        :target: https://travis-ci.org/AdrianWeishaeupl/autoflpy

.. image:: https://readthedocs.org/projects/autoflpy/badge/?version=latest
        :target: https://autoflpy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




AutoFLpy (Automated Flight Log python) is an open source code to allow you to create agile flight reports. This code rapidly creates flight reports for the user given an input file in a matter of minutes and is ideal for a complete analysis and evaluation of flight data. Multiple input data sources are accepted, with the report combining these into a succinct and overseeable document.


* Free software: GPLv3
* Documentation: https://autoflpy.readthedocs.io.

.. image:: images/Report_image.png
	:width: 700
	:alt: Image of a sample generated flight report.

Features
--------

* Generates a highly customisable and agile flight summary report using data from .log and input files.
* Default flight summary includes:
	* METAR information of the nearest airfield.
	* Checklist Information (if provided).
	* Plots for:
		* GPS altitude and velocity.
		* GPS latitude and longitude plotted on a map**.
		* Control inputs throughout the flight.
		* Barometric data throughout the flight.
		* Flight attitude throughout the flight.
		* Flight computer vibrational data.
		* Additional arduino data (if supplied).
* Multi-flight simultaneous analysis for comparing different flights.
* Sample data files included. This will be **created when the code is run for the first time**.
* Full choice of file paths for the data and outputs can be specified using the input file.

** For this feature to work, both geopandas and contextily need to be installed on the local machine. This needs to be done by the user due to difficulty installing these on various operating systems. A short help guide is attached in the installation instructions.

.. image:: images/SITL_flight_map.png
	:width: 700
	:alt: Image of a flight plotted over a map using AutoFLpy.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

Runways.csv adapted from https://github.com/sobester/ADRpy
