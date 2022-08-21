from collections import namedtuple

from .constant import LOG_LEVEL_MAP, YAML_EXT, JSON_EXT
from .log import log
from .merge import strategy_map

JamConfig = namedtuple(
    "JamConfig",
    ["loglvl", "input_paths", "output_path", "output_format", "array_strategy"],
)


def get_loglvl(verbosity):
    loglvl = LOG_LEVEL_MAP.get(verbosity, None)
    if loglvl is None:
        log.warn(f"Invalid verbosity level {verbosity}. Defaulting to debug.")
        return "debug"
    return loglvl.upper()


def get_output_format(args):
    output_format = "json"
    # Explicit flags takes precedence
    if args.json:
        return "json"
    if args.yaml:
        return "yaml"
    # if no flags, base it on the output suffix
    if args.output.suffix in JSON_EXT:
        return "json"
    if args.output.suffix in YAML_EXT:
        return "yaml"
    # If outputting to stdout use the first input file
    if args.input[0].suffix in JSON_EXT:
        return "json"
    if args.input[0].suffix in YAML_EXT:
        return "yaml"
    # Default to json
    return "json"


def load_config(args):
    return JamConfig(
        loglvl=get_loglvl(args.verbose),
        input_paths=args.input,
        output_path=args.output,
        output_format=get_output_format(args),
        array_strategy=strategy_map.get(args.array_strategy),
    )
