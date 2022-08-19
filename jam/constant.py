import pathlib
from collections import namedtuple

LOG_LEVEL_MAP = {0: "error", 1: "warning", 2: "info", 3: "debug"}

MAX_LOG_LEVEL = max(LOG_LEVEL_MAP.keys())

REF_TAG = "$ref"

STDIN = pathlib.Path("/dev/stdin")

STDOUT = pathlib.Path("/dev/stdout")
