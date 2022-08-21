import pathlib
import yaml
import pytest
import os

import jam.merge
import jam.util

test_case_path = pathlib.Path(os.path.realpath(__file__)).parent.joinpath('cases.yaml')

with open(test_case_path) as f:
    test_cases = yaml.safe_load(f)['merge']

@pytest.mark.parametrize('test_case', test_cases)
def test_merge(test_case):
    merged = None
    array_strategy = test_case.get('array_strategy', 'replace')
    strat = jam.merge.strategy_map.get(array_strategy)
    assert strat is not None

    for doc in test_case['docs']:
        merged = jam.merge.recurse_update(merged, doc, array_strat=strat)
    assert merged == test_case['expected']
