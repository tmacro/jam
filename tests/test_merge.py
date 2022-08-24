import pathlib
import yaml
import pytest
import os
import tempfile

import jam.merge
import jam.util
from jam.error import (
    JamError,
    ReferenceNotExistError,
    ReferenceResolutionError,
    ReferenceTypeMismatch,
    InvalidReferencedFile,
)

test_case_path = pathlib.Path(os.path.realpath(__file__)).parent.joinpath(
    "cases/merge.yaml"
)

with open(test_case_path) as f:
    test_cases = yaml.safe_load(f)


@pytest.mark.parametrize("test_case", test_cases)
def test_merge(test_case):
    merged = None
    array_strategy = test_case.get("array_strategy", "replace")
    strat = jam.merge.strategy_map.get(array_strategy)
    assert strat is not None

    for doc in test_case["docs"]:
        merged = jam.merge.recurse_update(merged, doc, array_strat=strat)
    assert merged == test_case["expected"]
