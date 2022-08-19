from collections import namedtuple

from .constant import LOG_LEVEL_MAP
from .log import log

JamConfig = namedtuple(
    "JamConfig",
    ["loglvl", "input_paths", "output_path"],
)


def get_loglvl(verbosity):
    loglvl = LOG_LEVEL_MAP.get(verbosity, None)
    if loglvl is None:
        log.warn(f"Invalid verbosity level {verbosity}. Defaulting to debug.")
        return "debug"
    return loglvl.upper()


def load_config(args):
    return JamConfig(
        loglvl=get_loglvl(args.verbose),
        input_paths=args.input,
        output_path=args.output,
    )
