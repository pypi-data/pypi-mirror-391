*************************
Installation and examples
*************************

*libadalina-analytics* can be installed using pip.

.. code-block::

   pip install libadalina-analytics

It is recommended to create a virtual environment before the installation of *libadalina-analytics* to avoid conflicts with other packages,
for example using `venv <https://docs.python.org/3/library/venv.html>`__ or `conda <https://anaconda.org/anaconda/conda>`__.

.. important::

    *libadalina-analytics* requires a Java Runtime Environment (JRE) installed on your system to run Apache Sedona,
    however, if a :code:`JAVA_HOME` environment variable is not set, *libadalina-analytics* will attempt to
    download, install and automatically use an OpenJDK 17 distribution in your home directory using the :code:`install-jdk` package.

.. toctree::

    /libadalina-examples/README.md