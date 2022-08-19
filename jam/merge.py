from collections.abc import Iterable, Mapping
from itertools import chain, zip_longest

from .util import is_iterable, is_mapping


def recurse_update(orig, new):
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
            k: recurse_update(orig.get(k), new.get(k))
            for k in set(chain(orig.keys(), new.keys()))
        }
    if is_iterable(orig) and is_iterable(new):
        return [recurse_update(o, n) for o, n in zip_longest(orig, new)]
    return new
