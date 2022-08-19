import json
import os.path
import pathlib
from collections.abc import Iterable, Mapping

from .log import log


def path_type(path):
    return pathlib.Path(os.path.expanduser(path)).resolve()


def is_mapping(data):
    return isinstance(data, Mapping)


def is_iterable(data):
    return (
        not isinstance(data, str)
        and not isinstance(data, bytes)
        and isinstance(data, Iterable)
    )


try:
    import yaml

    _file_loader = yaml.safe_load
    _file_dumper = yaml.safe_dump
    has_yaml = True
    log.info("Using YAML loader.")
except ImportError:
    _file_loader = json.load
    _file_dumper = json.dump
    has_yaml = False
    log.info("PyYaml not installed. Using JSON loader.")


def safe_read(path):
    try:
        with open(path) as f:
            return _file_loader(f)
    except Exception as e:
        log.exception("Error reading file")
    return None


def safe_dump(dumper, path, data):
    try:
        with open(path, "w") as f:
            return dumper(data, f)
    except Exception as e:
        log.exception("Error dumping data to file")
    return None


def safe_dump_json(path, data):
    return safe_dump(json.dump, path, data)


def safe_dump_yaml(path, data):
    return safe_dump(yaml.dump, path, data)
