from pathlib import Path

from .constant import REF_TAG, STDIN
from .error import (
    ReferenceNotExistError,
    ReferenceResolutionError,
    ReferenceTypeMismatch,
    InvalidReferencedFile,
)

from .log import log
from .util import is_listing, is_mapping, safe_read
import queue


def is_reference(doc):
    return is_mapping(doc) and doc.get(REF_TAG) is not None


def resolve_reference_path(parent_path, fragment):
    parent_path = Path(parent_path)
    fragment = Path(fragment)

    if fragment.is_absolute():
        return fragment
    try:
        return parent_path.parent.joinpath(fragment).resolve()
    except RuntimeError:
        raise ReferenceResolutionError(fragment, parent_path)


def read_reference(parent_path, fragment):
    resolved_path = resolve_reference_path(parent_path, fragment)
    if not resolved_path.exists():
        raise ReferenceNotExistError(fragment, parent_path, resolved_to=resolved_path)

    data = safe_read(resolved_path)
    if data is None:
        raise InvalidReferencedFile(fragment, parent_path, resolved_to=resolved_path)
    return resolved_path, data


def resolve_refs(parent_path, doc):
    # no reference resolution for stdin docs
    if parent_path == STDIN:
        log.warning("Skipping ref resolution for stdin doc.")
        return doc

    if is_reference(doc):
        # Check for other keys aside from $ref
        if len(doc) == 1:
            ref_path, data = read_reference(parent_path, doc[REF_TAG])
            log.info(f"Included reference: {doc[REF_TAG]}")
            log.info(f"  in: {parent_path.name}")
            log.info(f"  resolved to: {ref_path}")
            return resolve_refs(ref_path, data)
        else:  # Falls through to generic mapping logic
            log.warning(
                "Ambiguous reference found. Document contains keys other than $ref. Skipping resolution."
            )
            log.warning(f"  referenced path: {doc[REF_TAG]}")
            log.warning(f"  in: {parent_path}")

    if is_mapping(doc):
        return {k: resolve_refs(parent_path, v) for k, v in doc.items()}

    if is_listing(doc):
        return [resolve_refs(parent_path, v) for v in doc]

    return doc
