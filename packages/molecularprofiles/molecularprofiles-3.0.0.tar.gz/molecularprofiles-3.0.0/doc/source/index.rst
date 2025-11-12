:html_theme.sidebar_secondary.remove: true
:html_theme.sidebar_primary.remove: true

##########################################################
Meteorological Data Analysis Suite (``molecularprofiles``)
##########################################################

**Version**: |version| **Date**: |today|

This is ``molecularprofiles``, a Python package that will help with the analysis of molecular profile data
obtained from global data assimilation systems, like GDAS or ECMWF.

This library works with ``grib(1,2)`` or ``ecsv`` file formats, and is specifically designed
for the analysis of molecular content above the CTAO sites,
at El Roque de los Muchachos in the island of La Palma, and at Paranal in Chile.

**Key Features**:
   * Extract meteorological data and transform it from ``grib`` to ``ecsv`` format
   * Analyze these data and produce atmospheric models
   * Generate extinction input cards for the ``sim_telarray`` simulation package
   * Some other utilities for time-series analysis

**Authors**:
   - Initially created by Pere Munar-Adrover (pere.munaradrover@gmail.com).
   - Further development and maintenance

     * Mykhailo Dalchenko (mykhailo.dalchenko@unige.ch)
     * Georgios Voutsinas (georgios.voutsinas@unige.ch).

.. grid:: 1 2 2 2

    .. grid-item-card::

        :octicon:`gear;40px`

        Installation Guide
        ^^^^^^^^^^^^^^^^^^

        How to install molecularprofiles.

        +++

        .. button-ref:: installation
            :expand:
            :color: primary
            :click-parent:

            To the installation guide


    .. grid-item-card::

        :octicon:`code;40px`

        API Docs
        ^^^^^^^^

        The API docs contain detailed descriptions of
        of the various modules, classes and functions
        included in molecularprofiles.

        +++

        .. button-ref:: reference
            :expand:
            :color: primary
            :click-parent:

            To the API docs



.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: Contents:

   installation
   reference
