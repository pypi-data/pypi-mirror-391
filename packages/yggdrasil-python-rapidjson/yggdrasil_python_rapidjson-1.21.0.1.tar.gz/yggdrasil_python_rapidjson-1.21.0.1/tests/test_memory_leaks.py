# -*- coding: utf-8 -*-
# :Project:   python-rapidjson -- Tracemalloc-based leaks tests
# :Created:   dom 10 feb 2019 13:47:32 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   MIT License
# :Copyright: © 2019, 2025 Lele Gaifax
#

import io
import datetime
import gc
import sys

import pytest
import importlib
import yggdrasil_rapidjson as rj

tracemalloc = pytest.importorskip("tracemalloc")
# langmm: Increase in memory reported by gc.collect for
#   free-threaded python (3.14t). Maybe due to deferred reference
#   counting? Skip these tests when gil not enabled.
_is_gil_enabled = True
try:
    _is_gil_enabled = sys._is_gil_enabled()
except AttributeError:
    pass


@pytest.fixture(scope="session", autouse=True)
def import_external():
    r"""Import the external libraries so they don't contribute to the
    reference count."""
    packages = [
        'numpy', 'pandas', 'trimesh',
    ]
    for name in packages:
        try:
            importlib.import_module(name)
        except ImportError:
            pass


def object_hook(td):
    if '__td__' in td:
        return datetime.timedelta(td['__td__'])
    else:
        return td


def default(obj):
    if isinstance(obj, datetime.timedelta):
        return {"__td__": obj.total_seconds()}
    else:
        return obj


@pytest.mark.skipif(not _is_gil_enabled,
                    reason=("Memory leak test disabled for "
                            "free-threading python without GIL enabled "
                            "due to deferred reference counting"))
def test_object_hook_and_default():
    tracemalloc.start()

    data = []
    for i in range(1, 100):
        data.append({"name": "a%d" % i, "timestamp": datetime.timedelta(seconds=i)})

    snapshot1 = tracemalloc.take_snapshot().filter_traces((
        tracemalloc.Filter(True, __file__),))

    for _ in range(1000):
        a = rj.dumps(data, default=default)
        rj.loads(a, object_hook=object_hook)

    del a
    del _
    gc.collect()

    snapshot2 = tracemalloc.take_snapshot().filter_traces((
        tracemalloc.Filter(True, __file__),))

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    tracemalloc.stop()

    for stat in top_stats[:10]:
        # Uhm, with Py 3.14, on macOS,  the diff is 3...
        assert stat.count_diff <= 3


@pytest.mark.skipif(not _is_gil_enabled,
                    reason=("Memory leak test disabled for "
                            "free-threading python without GIL enabled "
                            "due to deferred reference counting"))
def test_load():
    tracemalloc.start()

    snapshot1 = tracemalloc.take_snapshot().filter_traces((
        tracemalloc.Filter(True, __file__),))

    for _ in range(10):
        dct = '{' + ','.join('"foo%d":"bar%d"' % (i, i) for i in range(100)) + '}'
        content = io.StringIO('[' + ','.join(dct for _ in range(100)) + ']')
        rj.load(content, chunk_size=50)

    del dct
    del content
    del _
    gc.collect()

    snapshot2 = tracemalloc.take_snapshot().filter_traces((
        tracemalloc.Filter(True, __file__),))

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    tracemalloc.stop()

    for stat in top_stats[:10]:
        # Uhm, with Py 3.14, on macOS,  the diff is 3...
        assert stat.count_diff <= 3


@pytest.mark.skipif(not _is_gil_enabled,
                    reason=("Memory leak test disabled for "
                            "free-threading python without GIL enabled "
                            "due to deferred reference counting"))
def test_failed_validation():
    tracemalloc.start()

    schema = """{
        "$schema": "http://json-schema.org/draft-04/schema#",
        "required": ["id", "name"],
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        }
    }""".encode("utf-8")

    obj = """{
        "id": 50
    }""".encode("utf-8")

    validate = rj.Validator(schema)

    snapshot1 = tracemalloc.take_snapshot().filter_traces((
        tracemalloc.Filter(True, __file__),))

    # start the test
    for j in range(1000):
        try:
            validate(obj)
        except rj.ValidationError:
            pass

    del j

    gc.collect()

    snapshot2 = tracemalloc.take_snapshot().filter_traces((
        tracemalloc.Filter(True, __file__),))

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    tracemalloc.stop()

    for stat in top_stats[:10]:
        # Uhm, with Py 3.14, on macOS,  the diff is 3...
        assert stat.count_diff <= 3
