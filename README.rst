============================
CardoAI Python Helper Module
============================

This library allows the utilization of different utility functions for different scenarios.

Main utils:

* time
* string
* data_structures
* db
* django
* math
* exception
* choices


Quick start
-----------
1. Import wanted function like this::

    from python_utils.time import date_range
    date_range(start_date, end_date)

Although the library provides some utility functions related to other libraries like django, it does not install any dependencies automatically.
This means, you can install the library even if you do not use these libraries, but keep in mind that in this case you cannot use the
functions that depend on them.

You can also chose to install the dependencies alongside the library, including the library in the requirements in the form::

    cardo-python-utils[django]

Tests
-----
The library has a high coverage by tests. If you want to see tests in action:

1. Inside venv, run  ``pip install -r tests/requirements.txt``

2. Run tests via ``pytest`` command
