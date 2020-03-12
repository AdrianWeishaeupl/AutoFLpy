.. highlight:: shell

============
Installation
============


Stable release
--------------

To install AutoFLpy, run this command in your terminal:

.. code-block:: console

    $ pip install autoflpy

This is the preferred method to install AutoFLpy, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for AutoFLpy can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/AdrianWeishaeupl/autoflpy

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/AdrianWeishaeupl/autoflpy/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/AdrianWeishaeupl/autoflpy
.. _tarball: https://github.com/AdrianWeishaeupl/autoflpy/tarball/master

Installing geopandas and contextily for map plotting
----------------------------------------------------

The easiest way to install `geopandas <https://geopandas.org/>`_ was found to be:

.. code-block:: console

	$ conda install --channel conda-forge geopandas

alternate ways can be found under the following link:
http://geopandas.org/install.html

The easiest way to install `contextily <https://github.com/darribas/contextily>`_ was found to be:

.. code-block:: console

	$ conda install contextily --channel conda-forge

alternate ways can be found under the following link:
https://stackoverflow.com/questions/54149384/how-to-install-contextily

