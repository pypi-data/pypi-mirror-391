
===========================
 yggdrasil-python-rapidjson
===========================

Python wrapper around YggdrasilRapidJSON
========================================

:Authors: Meagan Lang <langmm.astro@gmail.com>; Ken Robbins [RapidJSON] <ken@kenrobbins.com>; Lele Gaifax [RapidJSON] <lele@metapensiero.it>
:License: `MIT License <https://raw.githubusercontent.com/cropsinsilico/yggdrasil-python-rapidjson/yggdrasil/LICENSE>`_

YggdrasilRapidJSON_ is an extension to RapidJSON_, an extremely fast C++ JSON parser and serialization library. This package
wraps it into a Python C-extension, duplicating the functions/classes provided by `python-rapidjson <https://github.com/python-rapidjson/python-rapidjson>`_ and exposing the features added by YggdrasilRapidJSON_ including serialization/deserialization of additional datatypes, unitful scalars/arrays, and schema normalization/comparison.

.. TODO: Documentation link
.. TODO: https://python-rapidjson.readthedocs.io/en/latest


Getting Started
---------------

First install ``yggdrasil-python-rapidjson``:

.. code-block:: bash

    $ pip install yggdrasil-python-rapidjson

or, if you prefer `Conda <https://conda.io/docs/>`_:

.. code-block:: bash

    $ conda install -c conda-forge yggdrasil-python-rapidjson

Basic usage looks the same as python-rapidjson, with the exception of the package name (example adapted from python-rapidjson README.rst):

.. code-block:: python

    >>> import yggdrasil_rapidjson
    >>> data = {'foo': 100, 'bar': 'baz'}
    >>> yggdrasil_rapidjson.dumps(data)
    '{"foo":100,"bar":"baz"}'
    >>> yggdrasil_rapidjson.loads('{"bar":"baz","foo":100}')
    {'bar': 'baz', 'foo': 100}
    >>>
    >>> class Stream:
    ...   def write(self, data):
    ...      print("Chunk:", data)
    ...
    >>> yggdrasil_rapidjson.dump(data, Stream(), chunk_size=5)
    Chunk: b'{"foo'
    Chunk: b'":100'
    Chunk: b',"bar'
    Chunk: b'":"ba'
    Chunk: b'z"}'


Development
-----------

If you want to install the development version (maybe to contribute fixes or
enhancements) you may clone the repository:

.. code-block:: bash

    $ git clone --recursive https://github.com/cropsinsilico/yggdrasil-python-rapidjson.git

.. note:: The ``--recursive`` option is needed because we use a *submodule* to
          include YggdrasilRapidJSON_ sources. Alternatively you can do a plain
          ``clone`` immediately followed by a ``git submodule update --init``.

          Alternatively, if you already have (a *compatible* version of)
          YggdrasilRapidJSON includes around, you can compile the module specifying
          their location with the option ``--config-settings=cmake.define.RAPIDJSON_INCLUDE_DIRS=``, for example:

          .. code-block:: shell

             $ pip install . --config-settings=cmake.define.RAPIDJSON_INCLUDE_DIRS=/usr/include/rapidjson

The package can be built and installed from source via

.. code-block:: bash

    $ pip install .

The package tests and doctests can be run via pytest

.. code-block:: bash

    $ python -m pytest tests/ --doctest-glob="docs/*.rst" --doctest-modules docs

    
.. _YggdrasilRapidJSON: https://github.com/cropsinsilico/yggdrasil-rapidjson
.. _RapidJSON: http://rapidjson.org/
.. _PythonRapidJSON: https://github.com/python-rapidjson/python-rapidjson
