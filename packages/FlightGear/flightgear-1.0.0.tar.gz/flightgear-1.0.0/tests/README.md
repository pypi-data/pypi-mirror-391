# Running the unit tests

In order to run the tests, the package must be installed or at least its
modules accessible to Python (see the top-level `README.md`). Then the tests
can be run this way, from the root directory of the repository:

    python3 -m unittest

If you want to be more specific:

    python3 -m unittest tests.sgprops.test_sgprops
    python3 -m unittest tests.aircraft_catalogs.test_catalog
    python3 -m unittest tests.aircraft_catalogs.test_catalog.UpdateCatalogTests
    python3 -m unittest tests.aircraft_catalogs.test_catalog.UpdateCatalogTests.test_scan_set
    ...

Use the `-v` option after `python3 -m unittest` for verbose mode. For more
information, please refer to the
[documentation of the unittest module](https://docs.python.org/3/library/unittest.html).
