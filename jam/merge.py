from collections.abc import Iterable, Mapping
from itertools import chain, zip_longest
from collections import defaultdict

from .util import is_listing, is_mapping


def array_replace(orig, new):
    return new


def array_extend(orig, new):
    return list(chain(orig, new))


def array_merge(orig, new):
    return [
        recurse_update(o, n, array_strat=array_merge) for o, n in zip_longest(orig, new)
    ]


strategy_map = defaultdict(
    lambda: array_replace,
    {
        "replace": array_replace,
        "extend": array_extend,
        "merge": array_merge,
    },
)


def recurse_update(orig, new, array_strat=array_replace):
    """
    Given a nested dict/list combo, walk each and update orig with new,
    overwiting keys, and positions
    """
    if orig is None:
        return new
    if new is None:
        return orig
    if type(orig) != type(new):
        return new

    # Check for strings specifically because they cause problems with lists
    if isinstance(orig, str) and isinstance(new, str):
        return new
    if is_mapping(orig) and is_mapping(new):
        return {
            k: recurse_update(orig.get(k), new.get(k), array_strat=array_strat)
            for k in set(chain(orig.keys(), new.keys()))
        }
    if is_listing(orig) and is_listing(new):
        return array_strat(orig, new)
    return new
