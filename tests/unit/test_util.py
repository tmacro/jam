import pytest
from pathlib import Path
import os
import jam.util


def test_pathtype():
    assert jam.util.path_type("/") == Path("/")
    assert jam.util.path_type("~/foo") == Path(os.path.expanduser("~/foo"))
    assert jam.util.path_type("foo/") == Path("foo/").resolve()
    assert jam.util.path_type("-", allow_stdin=True) == Path("/dev/stdin")


def test_is_mapping():
    assert jam.util.is_mapping(dict()) == True
    assert jam.util.is_mapping(tuple()) == False
    assert jam.util.is_mapping(list()) == False
    assert jam.util.is_mapping("ddd") == False
    assert jam.util.is_mapping(True) == False
    assert jam.util.is_mapping(x for x in range(1)) == False


def test_is_listing():
    assert jam.util.is_listing(list()) == True
    assert jam.util.is_listing(tuple()) == True
    assert jam.util.is_listing(x for x in range(1)) == True
    assert jam.util.is_listing(dict()) == False
    assert jam.util.is_listing("ddd") == False
    assert jam.util.is_listing(True) == False
