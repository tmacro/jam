from pathlib import Path

from .constant import REF_TAG, STDIN
from .error import (
    ReferenceNotExistError,
    ReferenceResolutionError,
    ReferenceTypeMismatch,
)

from .log import log
from .util import is_iterable, is_mapping, safe_read


def _resolve_ref(parent_path, ref_path):
    parent_path = Path(parent_path)
    ref_path = Path(ref_path)

    if ref_path.is_absolute():
        if not ref_path.exists():
            log.error(f"Referenced absolute path does not exist {ref_path}")
            log.error(f"  in: {parent_path}")
            raise ReferenceNotExistError(ref_path, parent_path)
        log.info(f"Included reference {ref_path}")
        log.info(f"  in: {parent_path.name}")
        import_path = ref_path

    else:  # is relative path
        try:
            resolved = parent_path.parent.joinpath(ref_path)
        except ValueError:
            log.error(f"Referenced relative can not be resolved: {ref_path}")
            log.error(f"  in: {parent_path}")
            raise ReferenceResolutionError(ref_path, parent_path)
        if not resolved.exists():
            log.error(f"Referenced relative path does not exist: {ref_path}")
            log.error(f"  resolved to: {resolved}")
            log.error(f"  in: {parent_path}")
            raise ReferenceNotExistError(ref_path, parent_path, resolved_to=resolved)
        import_path = resolved
        log.info(f"Included reference: {ref_path}")
        log.info(f"  in: {parent_path.name}")
        log.info(f"  resolved to: {resolved}")

    imported = safe_read(import_path)
    if imported is None:
        log.error(f"Error reading referenced path {ref_path}!")
        log.error(f"  in: {parent_path}")
        raise JamError(f"Error reading referenced path {ref_path}")
    return import_path, imported


def _resolve_dict(parent_path, dikt):
    for key, value in dikt.items():
        if key == REF_TAG:
            imported_path, imported = _resolve_ref(parent_path, value)
            if is_mapping(imported):
                for _key, _value in _resolve_dict(imported_path, imported):
                    yield _key, resolve_refs(imported_path, _value)
            else:
                log.error(f"Reference resolved to list, expected dict!")
                log.error(f"  referenced path: {imported_path}")
                log.error(f"  in: {parent_path}")
                raise ReferenceTypeMismatch(imported_path, parent_path, "dict", "list")
        else:
            yield key, resolve_refs(parent_path, value)


def _resolve_list(parent_path, lst):
    for value in lst:
        if is_mapping(value) and value.get(REF_TAG) is not None:
            imported_path, imported = _resolve_ref(parent_path, value.get(REF_TAG))
            yield resolve_refs(imported_path, imported)
        else:
            yield resolve_refs(parent_path, value)


def resolve_refs(parent_path, doc):
    # no reference resolution for stdin docs
    if parent_path == STDIN:
        return doc
    if is_mapping(doc):
        return {k: v for k, v in _resolve_dict(parent_path, doc)}

    if is_iterable(doc):
        return [v for v in _resolve_list(parent_path, doc)]
    return doc
