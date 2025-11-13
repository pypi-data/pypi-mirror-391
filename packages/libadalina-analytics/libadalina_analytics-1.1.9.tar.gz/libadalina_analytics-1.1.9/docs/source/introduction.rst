
************
Introduction
************

*libadalina-analytics* is a Python library for spatial data analytics.

It provides analysis tools for

* building geospatial enriched graphs
* performing network analysis on geospatial data
* clustering geospatial area to create meaningful regions
* minimize facility relocations costs

It works with DataFrame and GeoDataFrame objects from *pandas* and *geopandas* libraries, and
makes use of Apache Sedona, a powerful geospatial processing engine, for efficient spatial data processing.

*libadalina-analytics* is part of the `ADaLinA project <https://expertise.unimi.it/resource/project/PNRR%5FBAC24ACESE%5F01>`__
that aims to develop a set of tools for the analysis of large-scale spatial data
to be integrated into the `Amelia homepage`_ platform.

The online documentation is available ad `<https://libadalinaanalytics-0bbfb4.gitlab.io>`__.

*libadalina-analytics* is partially funded by the European Union - Next Generation EU, Mission 4, Component 1 CUP J33C22002910001 - GRINS foundation, Project ADALINA.

Requirements
------------

*libadalina-analytics* requires Python 3.10 and depends on the following libraries:

* libadalina-core
* highspy
* pydantic
* scikit-learn

*libadalina-analytics* has been tested with OpenJDK 17.

.. _Amelia homepage: https://grins.it/progetto/piattaforma-amelia