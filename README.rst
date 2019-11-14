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




Automated flight log code. This code automatically creates flight logs for the user given an input file. It currently works with ardupilot log files taken from the flight computer in the .bin format and converted into the .log format using Mission Planner.


* Free software: GPLv3
* Documentation: https://autoflpy.readthedocs.io.


Features
--------

* Generates a highly customisable flight summary using data from log input files.
* Default flight summary includes:
	* METAR information of the nearest airfield.
	* Checklist Information (if provided).
	* Plots for:
		* GPS altitude and velocity.
		* GPS latitude and longitude.
		* Control inputs throughout the flight.
		* Barometric data throughout the flight.
		* Flight attitude throughout the flight.
		* Flight computer vibrational data.
		* Additional arduino data (if supplied).
* Sample data file included. This will be created when the code is run for the first time.
* Full choice of file paths for the data and outputs can be specified using the input file.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

Runways.csv taken from https://github.com/sobester/ADRpy
