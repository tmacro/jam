import pathlib
import yaml
import pytest
import os
import tempfile

import jam.reference
import jam.util
from jam.error import (
    JamError,
    ReferenceNotExistError,
    ReferenceResolutionError,
    ReferenceTypeMismatch,
    InvalidReferencedFile,
)

test_case_path = pathlib.Path(os.path.realpath(__file__)).parent.joinpath(
    "cases/reference.yaml"
)

with open(test_case_path) as f:
    test_cases = yaml.safe_load(f)


@pytest.fixture(scope="function")
def testdir():
    with tempfile.TemporaryDirectory() as td:
        yield pathlib.Path(td)

    # return pathlib.Path(tempfile.mkdtemp())


@pytest.fixture(scope="function", params=test_cases)
def ref_test_case(testdir, request):
    print(request.param["name"])
    for doc in request.param["docs"]:
        with open(testdir.joinpath(doc["path"]).as_posix(), "w") as f:
            yaml.dump(doc["content"], f)
    root_path = testdir.joinpath(request.param["root"])
    with open(root_path) as f:
        root_doc = yaml.safe_load(f)
    if request.param.get("xfail"):
        expected = None
    else:
        expected = request.param.get("expected")
    return root_path, root_doc, expected


def test_resolve_refs(ref_test_case):
    root_path, root_doc, expected = ref_test_case
    if expected is None:
        pytest.xfail(reason="Expected failure")
    try:
        resolved = jam.reference.resolve_refs(root_path, root_doc)
        if expected is not None:
            assert resolved == expected
    except ReferenceResolutionError as e:
        print("Encountered infinite loop resolving reference.")
        print(f"  referenced path: {e.ref_path}")
        print(f"  in: {e.parent_path}")
        raise
    except ReferenceNotExistError as e:
        print(f"Referenced relative path does not exist: {e.ref_path}")
        if e.resolved_to:
            print(f"  resolved to: {e.resolved_to}")
        print(f"  in: {e.parent_path}")
        raise
    except InvalidReferencedFile as e:
        print(f"Error reading referenced path {e.ref_path}!")
        if e.resolved_to:
            print(f"  resolved to: {e.resolved_to}")
        print(f"  in: {e.parent_path}")
        raise
